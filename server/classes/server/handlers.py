"""
the below functions were modified from https://github.com/SukkaW/pure-svg-countdown

---

MIT License

Copyright (c) 2021 Sukka

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from ..auction import AuctionContext

from tornado.web import RequestHandler
import utils, time, re, base64


def timer_handle(ctx):
    # type: (AuctionContext) -> type

    class TimerHandler(RequestHandler):
        def get(self):
            # css
            static= open(utils.DATA_DIR + "timer.css").read()
            static= re.sub(r'/\*.*?\*/', '', static, flags=re.DOTALL)

            dynamic= '\n'.join(get_style(ctx.META['end']))

            with open(utils.DATA_DIR + "bg_small_box.png", 'rb') as file:
                bg_img= base64.b64encode(file.read()).decode('utf-8')

            # svg
            resp= f"""
            <svg id="svg_main" fill="none" viewBox="0 0 399 168" xmlns="http://www.w3.org/2000/svg"
            width="399px" height="168px"
            >
              <foreignObject width="100%" height="100%">
              <style>{static} {dynamic}</style>
                <div xmlns="http://www.w3.org/1999/xhtml">
                  <div class="main" style="background: url(data:image/png;base64,{bg_img})">
                    <div class="contain">
                      <div class="title">Auction End:</div>
                      <br></br>
                      <div class="timer">
                        <span class="hours"></span>h
                        <span class="minutes"></span>m
                        <span class="seconds"></span>s
                      </div>
                    </div>
                  </div>
                </div>
              </foreignObject>
            </svg>
            """

            self.write(resp)
            self.set_header('content-type', 'image/svg+xml')

    def get_style(timestamp):
        styles= []

        rem= timestamp - time.time()
        total_seconds= rem

        # time calcs
        hours= int(rem // 3600)
        rem-= hours * 3600
        hour_delay= rem

        minutes= int(rem // 60)
        rem-= minutes * 60
        minute_delay= rem

        seconds= int(rem)

        # styles
        styles.append('.seconds::after { content: "%s"; animation-name: countdown-seconds; animation-duration: 60s; }' % seconds)
        styles.append('.minutes::after { content: "%s"; animation-name: countdown-minutes; animation-duration: 3600s; animation-delay: %ss }' % (minutes,minute_delay))
        styles.append('.hours::after { content: "%s"; animation-name: countdown-hours; animation-duration: 86400s; animation-delay: %ss }' % (hours,hour_delay))
        styles.append('.timer { opacity: 100%%; animation-name: timer-disappear; animation-duration: 1s; animation-timing-function:step-end;animation-direction: normal; animation-play-state: running; animation-fill-mode: forwards; animation-delay: %ss }' % (total_seconds-1))
        styles.append('.finish { opacity: 0%%; animation-name: finish-appear; animation-duration: 1s; animation-timing-function:step-end; animation-direction: normal; animation-play-state: running; animation-fill-mode: forwards; animation-delay: %ss }' % (total_seconds-1))

        styles.append(create_keyframes(seconds-1, 60, 'seconds'))
        styles.append(create_keyframes(minutes-1, 60, 'minutes'))
        styles.append(create_keyframes(hours-1, 24, 'hours'))

        return styles

    def create_keyframes(start, steps, name):
        ret= ''

        for i in range(steps):
            tmp1= f'{((100 / steps) * i):.2f}%'
            if start-i > 0:
                tmp2= start-i
            else:
                tmp2= steps + start - i

            ret+= f'{tmp1} {{ content: "{tmp2}" }}'

        if (tmp1 := start-steps+1) > 0:
            tmp2= tmp1
        else:
            tmp2= start+1
        ret+= f'100%{{ content: "{tmp2}" }}'

        ret= f'@keyframes countdown-{name} {{ {ret} }}'
        return ret

    return TimerHandler