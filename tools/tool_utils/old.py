def executable(fn):
    def ret(self, *args, execute=True, **kwargs):
        cmds= fn(self, *args, **kwargs)

        if execute:
            self.execute(cmds)
            return []
        else:
            return cmds

    return ret

class Tab:
    ISEKAI_URL= "https://hentaiverse.org/isekai/?s=Bazaar&ss=mm&filter=new"
    PERS_URL= "https://hentaiverse.org/?s=Bazaar&ss=mm&filter=new"

    USER_INPUT= "document.querySelector('input[list=hvut-mm-userlist]')"
    SUBJECT_INPUT= """document.querySelector("#hvut-mm-userlist").previousSibling"""
    BODY_INPUT= "document.querySelector('textarea[spellcheck=false]')"
    ITEM_SEARCH_INPUT= """document.querySelector('#hvut-mm-item > div > input[placeholder=Search]')"""
    EQUIP_SEARCH_INPUT= """document.querySelector('#hvut-mm-equip > div > input[placeholder=Search]')"""
    EQUIP_BUTTON= """document.querySelector('input[value=Equipment]')"""
    CURRENCY_BUTTON= """document.querySelector('input[value="Credits / Hath"]')"""

    def __init__(self, tab):
        self.tab= tab

    def to_isk(self):
        self.tab.set_url(self.ISEKAI_URL)

    def to_pers(self):
        self.tab.set_url(self.PERS_URL)


    @executable
    def set_main(self, user=None, subject=None, body=None):
        cmds= []
        if user:    cmds.append(f"{self.USER_INPUT}.value='{user}'")
        if subject: cmds.append(f"{self.SUBJECT_INPUT}.value='{subject}'")
        if body:    cmds.append(f"{self.BODY_INPUT}.value='{body}'")

        return cmds

    @executable
    def set_item(self, item, quant, price=0):
        cmds= []
        target_row= 'document.querySelector(".nosel.itemlist > tbody > tr:not(.hvut-none)")'

        cmds+= [
            f"{self.ITEM_SEARCH_INPUT}.value=\"{item}\"",
            f"{self.ITEM_SEARCH_INPUT}.dispatchEvent(new Event('input'))",
        ]
        cmds.append([
            f"{target_row}.querySelector('.hvut-mm-count').value= {int(quant)}",
            f"{target_row}.querySelector('.hvut-mm-price').value= {int(price)}",
            f"{target_row}.querySelector('input[type=checkbox]').click()"
        ])

        return cmds

    @executable
    def set_equip(self, equip):
        cmds= []
        target_row= 'document.querySelector(".nosel.equiplist > div:not(.hvut-none)")'

        # add as string in case these commands are added to the back of the set_main list
        # (because set_main acts on the landing view, and this command can be executed from there as well)
        cmds+= [
            f"{self.EQUIP_BUTTON}.click()"
        ]
        cmds.append([
            f"{self.EQUIP_SEARCH_INPUT}.value='{equip}'",
            f"{self.EQUIP_SEARCH_INPUT}.dispatchEvent(new Event('input'))"
        ])
        cmds.append([
            f"{target_row}.querySelector('input[type=checkbox]').click()"
        ])

        return cmds

    @executable
    def set_currency(self, credits=None):
        # inits
        c_row= "document.querySelector('#hvut-mm-credits')"
        cmds= []

        # open currency section
        cmds+= [
            f"{self.CURRENCY_BUTTON}.click()"
        ]

        # attach credits
        if credits:
            cmds.append([
                f"{c_row}.querySelector('.hvut-mm-count').value={credits}",
                f"{c_row}.querySelector('[type=checkbox]').click()"
            ])

        # return
        return cmds

    # evaluates "groups" of JS strings, where each group is formed by joining consecutive strings in cmds
    # list instances within cmds are treated as their own group
    def execute(self, cmds):
        def exec(lst):
            if not lst: return
            tmp= ';\n'.join(lst)

            # print(f'executing\n...\n{tmp}\n...')
            self.tab.evaluate(tmp)

        lst= []
        for x in cmds:
            if isinstance(x, list):
                exec(lst)
                lst= []

                exec(x)
                continue
            else:
                lst.append(x)
                if x is cmds[-1]:
                    exec(lst)
                    lst= []
                    continue

        assert lst == [], str(lst)

    # def execute(self, cmds):
    #     # await new Promise(r => setTimeout(r, 2000));
    #     def exec(lst):
    #         if not lst: return ""
    #         tmp= ';\n'.join(lst)
    #
    #         # print(f'executing\n...\n{tmp}\n...')
    #         return tmp
    #
    #     slp= "\n; await new Promise(r => setTimeout(r, 500));\n"
    #     cmd= []
    #     lst= []
    #     for x in cmds:
    #         if isinstance(x, list):
    #             cmd.append(exec(lst))
    #             lst= []
    #
    #             cmd.append(exec(x))
    #             continue
    #         else:
    #             lst.append(x)
    #             if x is cmds[-1]:
    #                 cmd.append(exec(lst))
    #                 lst= []
    #                 continue
    #
    #     cmd= slp + slp.join(cmd)
    #     self.tab.evaluate(cmd)
    #     print(f".....\n{cmd}\n.....")
    #     assert lst == [], str(lst)


class TabGenerator:
    def __init__(self, chrome, n=9):
        self.n= n
        self.ind= 0
        self.chrome= chrome

        self.tabs= [Tab(x) for x in reversed(chrome.tabs) if x.title == "about:blank"]
        if not self.tabs:
            self.tabs+= self.create_tabs()

    def create_tabs(self):
        return [Tab(self.chrome.add_tab()) for i in range(self.n)]

    def get_tab(self):
        if self.ind >= len(self.tabs):
            self.tabs+= self.create_tabs()

        self.ind+= 1
        return self.tabs[self.ind-1]