from tornado.web import RequestHandler
from ..auction import AuctionContext, EquipScraper



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
                    eq['code']= code
                    eq['name']= data['name']
                    eq['link']=  link

                    bid_info= bid_cat.get(code, {})
                    eq['current_bid']= bid_info.get('visible_bid', 0)

                    ret['items'].append(eq)

            self.write(ret)

        # proxy bid submissions
        def post(self):

            pass

        # allow CORS
        def options(self):
            pass

    return FormHandler


# def validate_bid()