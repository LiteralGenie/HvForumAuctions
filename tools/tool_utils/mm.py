from __future__ import annotations

import copy
import dataclasses
import json
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Union, List, Dict

from bs4 import BeautifulSoup
from requests import Session, Response

# @todo: logging
# @todo: hath
# @todo: sent / read / inbox


class MaybeIsekai:
    isekai: bool

    @property
    def base_link(self):
        ret = f"https://hentaiverse.org/"
        ret += "isekai/" if self.isekai else ""
        return ret

    @property
    def new_link(self):
        return self.base_link + "?s=Bazaar&ss=mm&filter=new"


class HvSession:
    HV_LINK = "https://hentaiverse.org"
    LOGIN_LINK = "https://forums.e-hentai.org/index.php?act=Login&CODE=01"
    RATE_LIMIT = 1 # seconds btwn requests
    ign: str = None

    did_login: bool = False
    _has_isekaid: bool = False # isekai cookies set

    def __init__(self, user, pw, session: Session = None):
        self.user = user
        self.pw = pw

        self.session = session or Session()
        self._last_sent = 0

    def login(self):
        invalid_string = "You have to log on to access this game."

        resp = self.get(self.HV_LINK)
        if invalid_string in resp.text:
            self._login()

        self.did_login = True
        return self

    def _login(self):
        print('Logging into HV...')
        payload = dict(
            CookieDate=1,
            b='d',
            bt=6,
            UserName=self.user,
            PassWord=self.pw,
            ipb_login_submit="Login!",
        )

        resp = self.post(self.LOGIN_LINK, data=payload)
        resp.encoding = 'utf-8'
        assert "You are now logged in as:" in resp.text

        ign = re.search("You are now logged in as: (.*?)<br", resp.text)
        self.ign = ign.group(1)

        return self.session

    def get(self, url: str, **kwargs):
        self._prep_truck(url)
        self._delay_request()

        # print(f'Getting {url} -- {kwargs}')
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs):
        self._prep_truck(url)
        self._delay_request()

        # print(f'Posting {url} -- {kwargs}')
        return self.session.post(url, **kwargs)

    def _delay_request(self):
        elapsed = time.time() - self._last_sent

        if elapsed < self.RATE_LIMIT:
            delay = self.RATE_LIMIT - elapsed
            time.sleep(delay)

        self._last_sent = time.time()
        return

    # visit isekai at least once after login to set cookies or something
    def _prep_truck(self, url: str):
        if '/isekai/' in url and not self._has_isekaid:
            self._has_isekaid = True
            self.get('https://hentaiverse.org/isekai/')


@dataclass
class MmPayload:
    action: str
    action_value: int
    select_item: int
    select_count: int
    select_pane: Union[int, str]

    mmtoken: str = None
    message_to_name: str = ""
    message_body: str = ""
    message_subject: str = ""

    def dict(self, token: str = None):
        ret = dataclasses.asdict(self)
        ret['mmtoken'] = token or self.mmtoken
        return ret

class PayloadEnum(Enum):
    # action
    DETACH_ACTION = "attach_remove"
    ATTACH_ACTION = "attach_add"
    COD_ACTION = "attach_cod"
    SEND_ACTION = "send"

    # select_pane
    ITEM_PANE = "item"
    EQUIP_PANE = "equip"
    CREDITS_PANE = "credits"
    HATH_PANE = "hath"

class MmLoc(Enum):
    # msg location
    OUT_BOX = "sent"
    IN_BOX = "inbox"
    READ_BOX = "read"

@dataclass
class Item:
    code: int
    name: str
    quant: int

    def __str__(self):
        return f"[{self.code}] {self.quant}x {self.name}"

@dataclass
class PartialEquip:
    name: str

@dataclass
class PartialItem:
    name: str
    quant: int

@dataclass
class Equip:
    eid: int
    key: str
    name: str

    isekai: bool

    in_inv: bool = None
    locked: bool = None

    @property
    def _base_link(self):
        ret = "https://hentaiverse.org/"
        ret += "isekai/" if self.isekai else ""
        return ret

    @property
    def link(self):
        return self._base_link + f"equip/{self.eid}/{self.key}"

    def __str__(self):
        l = " (locked)" if self.in_inv and self.locked else ""
        return f"{self.name}{l} -- {self.link}"

    @staticmethod
    def parse_script(dynjs_script: str, isekai: bool) -> dict:
        # clean
        ret = dict()
        reps = [';', 'var dynjs_equip=', 'var dynjs_eqstore =']
        data = re.sub(rf"(?:{'|'.join(reps)})", "", dynjs_script)
        data = json.loads(data)

        # parse
        for eid,dct in data.items():
            eid = int(eid)
            ret[eid] = Equip(
                eid=eid, key=dct['k'], name=dct['t'],
                isekai=isekai,
            )

        # return
        return ret

PartialList = List[Union[PartialItem, PartialEquip]]
AttachList = List[Union[Item, Equip]]


# detailed equip info (for equips in inventory) is kept in a .js file separate from the html
# this class serves as a cache for that info and fetches that data whenever new equips appear
class EquipInfo:
    link: str = None
    cache: Dict[int, Equip] = dict()

    def __init__(self, session: HvSession, isekai: bool):
        self.session = session
        self.isekai = isekai

    def get(self, eid: int):
        self.cache[eid] = self.cache.get(eid) or self._load(eid)
        return copy.copy(self.cache[eid])

    def _load(self, target_eid: int):
        # fetch
        assert self.link, 'no dynjs link supplied'
        resp = self.session.get(self.link)

        # parse
        data = Equip.parse_script(resp.text, self.isekai)
        self.cache.update(data)

        # return
        return self.cache[target_eid]

class MmMessage(MaybeIsekai):
    """DO NOT use __init__, use MmState.fetch_whatever or MmMessage.from_id instead"""

    # fields known regardless of how the instance was constructed
    # (eg from an inbox page vs from the id directly)
    session: HvSession
    id: int
    sender: str
    rcvr: str
    subject: str

    location: MmLoc
    is_return: bool

    # only guaranteed if message was retrieved from inbox / outbox / read-box
    # (ie MmState._fetch_page)
    sent: str = None # @todo: int timestamp
    read: str = None

    # fetched as necessary
    _body: str = None
    _attachments: Union[AttachList, PartialList] = None


    def __init__(self, session: HvSession, isekai: bool):
        self.session = session
        self.isekai = isekai

    @property
    def body(self):
        if not self._body:
            self.reload()
        return self._body

    @property
    def attachments(self) -> Union[AttachList, PartialList]:
        if not self._attachments:
            self.reload()
        return self._attachments

    def reload(self):
        data = self.from_id(self.session, self.id, self.isekai)
        self.__dict__.update(data.__dict__)

    # get message details
    @classmethod
    def from_id(cls, session: HvSession, mid: int, isekai: bool) -> MmMessage:
        # fetch
        base_link = "https://hentaiverse.org/"
        base_link += "isekai/" if isekai else ""

        url = base_link + "?s=Bazaar&ss=mm&filter=sent&mid=" + str(mid)
        resp = session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # scrape
        pane = soup.select_one('#mmail_left')
        fields = pane.select('input[type=text]')

        [rcvr, sender, subject] = [x['value'] for x in fields]
        body = pane.select_one('textarea').text
        attachments = cls.parse_attachments(soup, isekai)

        # return
        mm = cls(session, isekai)
        mm.id = mid

        if sender == "MoogleMail":
            mm._load_return(rcvr, sender, subject, body, attachments)
        else:
            mm._load_normal(rcvr, sender, subject, body, attachments)

        return mm

    # mails that weren't returned
    def _load_normal(self, rcvr, sender, subject, body, attachments):
        # type: (str, str, str, str, AttachList) -> None

        # set basic stuff
        self.sender = sender
        self.rcvr = rcvr
        self.subject = subject
        self.is_return = False

        # set body / attachments -- will depend on whether the items (if any) have been detached
        [partials, real_body, _] = self.parse_body(body)
        assert not partials or not attachments

        self._body = real_body
        if self._attachments is None:
            self._attachments = attachments or partials

        # set location
        # if self is sender, then outbox
        assert self.session.ign in [sender, rcvr]
        if sender == self.session.ign:
            self.location = MmLoc.OUT_BOX
        # else either inbox or read box
        else:
            # inbox messages will have attachments
            # (ones without will have moved to read as a result of this function)
            if attachments:
                self.location = MmLoc.IN_BOX
            else:
                self.location = MmLoc.READ_BOX


    def _load_return(self, rcvr, sender, subject, body, attachments):
        # type: (str, str, str, str, AttachList) -> None

        # set basic stuff
        self.sender = rcvr
        self.subject = subject.replace("[RTS] ", "")
        self.is_return = True

        # body / attachments will depend on whether the items (if any) have been detached
        [partials, real_body, real_rcvr] = self.parse_body(body)
        assert not partials or not attachments

        self.rcvr = real_rcvr
        self._body = real_body
        if self._attachments is None:
            self._attachments = attachments or partials

        # inbox messages will have attachments
        # (ones without will have moved to read as a result of this function)
        if attachments:
            self.location = MmLoc.IN_BOX
        else:
            self.location = MmLoc.READ_BOX

    # NOTE: returns empty list if attachments already detached
    @staticmethod
    def parse_attachments(soup: BeautifulSoup, isekai: bool) -> AttachList:
        # inits
        ret = []
        lst = soup.select_one('#mmail_attachlist')

        # return if no attachments
        if lst is None:
            return []

        # get equips
        eq_script = soup.select_one('#mmail_attachinfo > script')
        eq_data = Equip.parse_script(eq_script.contents[0], isekai)
        ret += list(eq_data.values())

        # get items
        it_divs = lst.select('div[onmouseout="common.hide_popup_box()"]')
        for div in it_divs:
            code = re.search(r"'right','?(\d+)", div['onmouseover'])
            code = int(code.group(1))

            m = re.search('(\d+)x (.*)', div.text)
            quant, name = m.groups()

            ret.append(Item(code=code, name=name, quant=quant))

        # check count
        count = soup.select_one('#mmail_attachcount').text
        count = re.search('(\d+) / 10 items attached', count)
        count = int(count.group(1))
        assert count == len(ret), f'parsed {len(ret)}x attachments, but missing {count-len(ret)}x'

        # return
        return ret

    @staticmethod
    def parse_body(body: str) -> List[Union[PartialList, str]]:
        lines = body.splitlines()
        real_body = lines
        real_rcvr = None
        partials = []

        for i,l in enumerate(lines[::-1]):
            if m := re.search(r'Removed Attachment: ([\w\s]+)', l):
                partials.append(PartialEquip(m.group(1)))
            elif m := re.search(r'Removed Attachment: (\d+)x (.*)', l):
                partials.append(PartialEquip(m.group(1)))
            elif m := re.search("This message was returned from (.*), kupo!", l):
                real_rcvr = m.group(1)
            elif not l.strip():
                continue
            else:
                if i > 0:
                    real_body = lines[:-i]
                break

        real_body = "\n".join(real_body)
        return [partials, real_body, real_rcvr]

    @property
    def from_self(self) -> bool:
        return self.is_return or (self.session.ign == self.sender)

    @property
    def finalized(self) -> bool:
        return any([
            self.read is not None,
            len(self.attachments) == 0,
            all(isinstance(x, PartialEquip) or isinstance(x, PartialItem) for x in self.attachments)
        ])

    def __str__(self):
        rtrn = "RTS | " if self.is_return else ""
        return f"[{rtrn}{self.sender} to {self.rcvr}] {self.subject}"

class MmState(MaybeIsekai):
    eq_info: EquipInfo
    mails: Dict[int, MmMessage]

    items: List[Item] = []
    equips: List[Equip] = []
    credits: int = None
    hath: int = None
    cod: int = 0

    token: str
    token_simple: str
    uid: int
    attachments: AttachList

    def __init__(self, session: HvSession, isekai=False):
        self.isekai = isekai
        self.session = session
        self.eq_info = EquipInfo(session=session, isekai=isekai)

        self.reload()

    def reload(self, resp: Response = None, soup: BeautifulSoup = None):
        # fetch page
        if soup is None:
            if resp is None:
                resp = self.session.get(self.new_link)
            soup = BeautifulSoup(resp.text, 'html.parser')

        self.token = self._parse_token(soup=soup)
        self.token_simple = self._parse_simple_token(soup=soup)
        self.items = self._parse_items(soup=soup)
        self.equips = self._parse_equips(soup=soup)
        self.uid = self._parse_uid(soup=soup)
        self.attachments = MmMessage.parse_attachments(soup, self.isekai)
        self.credits = self._parse_credits(soup=soup)
        self.cod = self._parse_cod(soup=soup)

    def _parse_credits(self, soup: BeautifulSoup) -> int:
        # scrape
        credits = soup.select_one('#mmail_attachcredits')
        if credits:
            credits = re.search('Current Funds: ([\d,]+) Credits', credits.text)
            credits = credits.group(1).replace(",", "")
            credits = int(credits)
        else:
            credits = -1

        # return
        return credits

    def _parse_cod(self, soup: BeautifulSoup) -> int:
        # scrape
        cod = soup.select_one('#newcod')
        cod = int(cod['value']) if cod else 0

        # return
        return cod

    def _parse_token(self, soup: BeautifulSoup) -> str:
        # get token
        token = soup.select_one('input[name=mmtoken]')
        token = token['value']

        # return
        return token

    def _parse_uid(self, soup: BeautifulSoup) -> int:
        # get token
        script = soup.select_one('#mainpane > script')
        uid = re.search('var uid = (\d+)', str(script))
        uid = int(uid.group(1))

        # return
        return uid

    def _parse_simple_token(self, soup: BeautifulSoup) -> str:
        # get token
        script = soup.select_one('#mainpane > script')
        token = re.search(f'var simple_token = "([^\s]+)"', str(script))
        token = token.group(1)

        # return
        return token

    def _parse_items(self, soup: BeautifulSoup) -> List[Item]:
        # inits
        items = []
        rows = soup.select('.itemlist > tr')

        # loop items
        for r in rows:
            name = r.select_one('td > div').text

            code = r.select_one('td > div')['onclick']
            code = re.search(r'set_mooglemail_item\((\d+),', code)
            code = int(code.group(1))

            quant = r.select_one('td:nth-child(2)').text
            quant = int(quant)

            items.append(Item(name=name, quant=quant, code=code))

        self.items = items
        return self.items

    def _parse_equips(self, soup: BeautifulSoup) -> List[Equip]:
        # inits
        equips = []

        # update equip cache
        info_link = soup.select_one('#mainpane > script:last-child')['src']
        self.eq_info.link = self.base_link + info_link

        # get equips
        rows = soup.select('.eqp > div[data-locked]')
        for r in rows:
            eid = int(r['id'][1:])
            locked = (r['data-locked'] == "1")

            eq = self.eq_info.get(eid)
            eq.locked = locked
            eq.in_inv = True

            equips.append(eq)

        # return
        return equips

    def get_item(self, name: str, default=None, throw=False):
        try:
            return next(x for x in self.items if x.name.lower() == name.lower())
        except StopIteration:
            if throw:
                raise KeyError(f'no item with name: {name}')
            else:
                return default

    def get_equip(self, eid: int, default=None, throw=False):
        try:
            return next(x for x in self.equips if x.eid == eid)
        except StopIteration:
            if throw:
                raise KeyError(f'no eq with eid: {eid}')
            else:
                return default

    def fetch_inbox(self, start=0, end=0):
        return self._fetch_mails(MmLoc.IN_BOX, start, end)
    def fetch_read(self, start=0, end=0):
        return self._fetch_mails(MmLoc.READ_BOX, start, end)
    def fetch_sent(self, start=0, end=0):
        return self._fetch_mails(MmLoc.OUT_BOX, start, end)

    def _fetch_mails(self, loc: MmLoc, start=0, end=0):
        ret = []
        for i in range(start, end+1):
            mails = self._fetch_page(loc, i)
            ret += mails

            if len(mails) == 0:
                break
        return ret

    def _fetch_page(self, loc: MmLoc, ind: int) -> List[MmMessage]:
        # fetch
        url = self.base_link + f"?s=Bazaar&ss=mm&filter={loc}&page={ind}"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # inits
        ret = []
        is_outbox = (loc is MmLoc.OUT_BOX)
        rows = soup.select('#mmail_list > tr')

        # parse
        for r in rows[1:]:
            mm = MmMessage(self.session, self.isekai)
            vals = [x.text for x in r.select('td')]

            id_ = re.search('&mid=(\d+)', r['onclick'])
            mm.id = int(id_.group(1))

            mm.location = loc
            mm.subject = vals[1].replace("[RTS] ", "")
            mm.sent = vals[2]
            mm.read = vals[3]

            name = vals[0]
            mm.sender = self.session.ign if is_outbox else name
            mm.rcvr = name if is_outbox else self.session.ign
            mm.is_return = True if (name == "MoogleMail" and not is_outbox) else False

            ret.append(mm)

        return ret

    def get_mail(self, mid: int) -> MmMessage:
        # fetch
        self.mails[mid] = self.mails[mid] or MmMessage.from_id(self.session, mid, self.isekai)
        mail = self.mails[mid]

        # update
        if not mail.finalized:
            mail.reload()

        # return
        return mail


class MoogleMail:
    def __init__(self, session: HvSession, isekai=False):
        self.session = session
        self.state = MmState(self.session, isekai=isekai)
        self.detach_all()

    def detach_all(self) -> None:
        # check for attachments
        if len(self.state.attachments) == 0:
            return

        # detach
        payload = MmPayload(
            action=PayloadEnum.DETACH_ACTION.value,
            action_value=0,
            select_item=0,
            select_count=0,
            select_pane=0,
        ).dict(token=self.state.token)
        resp = self.session.post(self.state.new_link, data=payload)

        # update state
        self.state.reload(resp)

    def send(self, user: str, subject: str, body=""):
        # payload
        payload = MmPayload(
            action=PayloadEnum.SEND_ACTION.value,
            action_value=0,
            select_item=0,
            select_count=0,
            select_pane=0,
            message_to_name=user,
            message_subject=subject,
            message_body=body,
        ).dict(token=self.state.token)

        # send
        resp = self.session.post(self.state.new_link, data=payload)
        assert "Your message has been sent." in resp.text

        # update state
        self.state.reload()

    def attach_item(self, name: str, quant: int):
        # get item
        item = self.state.get_item(name, throw=True)

        # check quantity
        assert quant <= item.quant, f"tried to attach [{quant}x {name}] but only [{item.quant}x] in inventory"

        # attach
        payload = MmPayload(
            action=PayloadEnum.ATTACH_ACTION.value,
            action_value=0,
            select_item=item.code,
            select_count=quant,
            select_pane=PayloadEnum.ITEM_PANE.value,
        ).dict(self.state.token)
        resp = self.session.post(self.state.new_link, data=payload)

        # update state
        old_count = item.quant
        self.state.reload(resp)

        # assertions
        new_item = self.state.get_item(name)
        if new_item:
            assert new_item.quant == old_count - quant, f"attached [{quant}x {name}] of [{old_count}x] but [{new_item.quant}x] remains"

    def attach_equip(self, eid: int):
        # get item
        eq = self.state.get_equip(eid, throw=True)

        # unlock
        if eq.locked:
            self.unlock(eid)
            eq.locked = False

        # attach
        payload = MmPayload(
            action=PayloadEnum.ATTACH_ACTION.value,
            action_value=0,
            select_item=eid,
            select_count=1,
            select_pane=PayloadEnum.EQUIP_PANE.value,
        ).dict(self.state.token)

        # send
        resp = self.session.post(self.state.new_link, data=payload)

        # update state
        self.state.reload(resp)

        # assertions
        eq = self.state.get_equip(eid)
        assert eq is None, f'equip not attached: [{eq}]'

    def unlock(self, eid: int, lock=False):
        # get equip
        eq = self.state.get_equip(eid, throw=True)

        # if already locked / unlocked, you're doing something wrong.
        if bool(eq.locked) == lock:
            verb = "locked" if lock else "unlocked"
            raise Exception(f"[{eq.eid} | {eq.name}] is already {verb}")

        # payload
        url = self.state.base_link + "json"
        payload = dict(
            eid = eid,
            lock = 1 if lock else 0,
            method = "lockequip",
            token = self.state.token_simple,
            type = "simple",
            uid = self.state.uid,
        )

        # send
        resp = self.session.post(url, json=payload)
        assert "error" not in json.loads(resp.text), f"bad response:\n{resp.text}\nwith payload:\n{payload}"

        # update state
        eq.locked = lock

    def set_cod(self, cod: int):
        # at least one item must be attached
        assert len(self.state.attachments) > 0, "cannot set CoD before any items are attached"

        # set
        payload = MmPayload(
            action = PayloadEnum.COD_ACTION.value,
            action_value=cod,
            select_item=0,
            select_count=0,
            select_pane=0,
        ).dict(token=self.state.token)

        # send
        resp = self.session.post(self.state.new_link, data=payload)

        # update state
        self.state.reload(resp)

        # assertions
        assert self.state.cod == cod

    def set_credits(self, credits: int, verify=False):
        # set
        payload = MmPayload(
            action = PayloadEnum.ATTACH_ACTION.value,
            action_value=0,
            select_item=0,
            select_count=credits,
            select_pane=PayloadEnum.CREDITS_PANE.value,
        ).dict(token=self.state.token)

        # send
        resp = self.session.post(self.state.new_link, data=payload)

        # update state
        old_credits = self.state.credits
        self.state.reload(resp)

        # disable verify if it's possible that you'll receive credits (eg from a CoD acceptance)
        if verify:
            assert self.state.credits == old_credits - credits, f'unexpected credit balance: {self.state.credits} =/= {old_credits} - {credits}'