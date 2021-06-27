"""
Example server reponse to GET
{
  "increment": 25,
  "items": [
    {
      "cat": "Wep",
      "code": "1",
      "name": "Legendary Ethereal Shortsword of Slaughter",
      "current_bid": 50,
      "bidder": "blah",
      "link": "https://hentaiverse.org/isekai/equip/50773/41b3481860"
    },
    {
      "cat": "Wep",
      "code": "3",
      "name": "Legendary Power Helmet of Slaughter",
      "current_bid": 0,
      "bidder": "",
      "link": "https://hentaiverse.org/isekai/equip/50773/41b3481860"
    }
  ]
}

Example client POST data
{ 
    "user": blahblah
    "items": [
        { "cat": "Wep", "code": "1", "bid": 25000},
        { "cat": "Arm", "code": "3", "bid": 123458},
    ]
}
"""

from tornado.web import RequestHandler
from ..auction import AuctionContext, EquipScraper
import json


def handle_proxy(ctx):
    # type: (AuctionContext) -> type
    class FormHandler(RequestHandler):
        def set_default_headers(self):
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Headers", "*")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.set_header('Content-type', 'application/json')

        # summarize and repackage meta / bid info for frontend
        def get(self):
            ret= dict(
                increment=ctx.CONFIG['min_bid_increment'],
                items=[],
            )

            # iterate categories
            max_bids= ctx.get_max_bids()
            for dct in ctx.META['equips']:
                cat= dct['abbreviation']
                bid_cat= max_bids.get(cat, {})

                # iterate equips
                for code,link in dct['items'].items():
                    eid= EquipScraper.extract_id_key(link)[0]
                    data= ctx.EQUIPS[eid]

                    eq= dict()
                    eq['cat']= cat
                    eq['code']= str(code)
                    eq['name']= data['name']
                    eq['link']=  link

                    bid_info= bid_cat.get(code, {})
                    eq['current_bid']= bid_info.get('visible_bid', 0)

                    ret['items'].append(eq)

            self.write(ret)

        # proxy bid submissions
        def post(self):
            # todo: log POST / validation error
            data= json.loads(self.request.body.decode('utf-8'))
            validate_POST(data)

            result= ctx.create_proxy_bids(data)
            self.write(result['key'])

        # allow CORS
        def options(self):
            pass

    return FormHandler


def validate_POST(data):
    # check username
    assert str(data['user']), "empty username"

    # check item dicts
    for it in data['items']:
        for word in ['cat', 'code', 'bid']:
            # check key existence
            assert word in it, f'missing key: {word}'
            # check non-empty
            assert str(it[word]), f'empty value for key: {word}'

        # check for numerical, positive bid
        assert type(it['bid']) == int, f'bid is not an int: {it["bid"]}'
        assert it['bid'] > 0, f'bid is negative: {it["bid"]}'