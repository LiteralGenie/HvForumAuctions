/*
timer design and code was modified from https://github.com/SukkaW/pure-svg-countdown

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
*/


<template>
  <img src="http://localhost:8113/timer"/>
  <svg fill="none" viewBox="0 0 399 168" xmlns="http://www.w3.org/2000/svg">
    <foreignObject width="100%" height="100%">
      <div xmlns="http://www.w3.org/1999/xhtml">
        <div class="main">
          <div class="contain">
            <div class="title">Auction End:</div>
            <br>
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
</template>


<script>
import { buildSvg } from "./timer_utils.js"

export default {
  name: 'timer',
  data() { return {
    hour_style: { color: 'red' }
  }},
  created() {
    let styles= buildSvg(1625115766*1000) //([2021, 7, 5])
    let sheet= window.document.styleSheets[0];

    styles.forEach(s => {
      console.log(s)
      sheet.insertRule(s, sheet.cssRules.length);
    })
  }
}
</script>


<style scoped>
  div {
    display: block
  }

  svg {
    width: 399px;
    height: 168px;
  }

  .main {
    height: 168px;
    background-image: url('~@/assets/bg_small_box.png');
  }

  .contain {
    position: relative;
    height: 100%;
  }

  .title, .timer {
    position: absolute;
    width: 399px;

    color: white;
    text-align: center;

    /* 3px outline -- https://stackoverflow.com/a/58832933 */
    text-shadow: -3px -3px 0px #000,
    -3px -2px 0px #000,
    -3px -1px 0px #000,
    -3px 0px 0px #000,
    -3px 1px 0px #000,
    -3px 2px 0px #000,
    -3px 3px 0px #000,
    -2px -3px 0px #000,
    -2px -2px 0px #000,
    -2px -1px 0px #000,
    -2px 0px 0px #000,
    -2px 1px 0px #000,
    -2px 2px 0px #000,
    -2px 3px 0px #000,
    -1px -3px 0px #000,
    -1px -2px 0px #000,
    -1px -1px 0px #000,
    -1px 0px 0px #000,
    -1px 1px 0px #000,
    -1px 2px 0px #000,
    -1px 3px 0px #000,
    0px -3px 0px #000,
    0px -2px 0px #000,
    0px -1px 0px #000,
    0px 1px 0px #000,
    0px 2px 0px #000,
    0px 3px 0px #000,
    1px -3px 0px #000,
    1px -2px 0px #000,
    1px -1px 0px #000,
    1px 0px 0px #000,
    1px 1px 0px #000,
    1px 2px 0px #000,
    1px 3px 0px #000,
    2px -3px 0px #000,
    2px -2px 0px #000,
    2px -1px 0px #000,
    2px 0px 0px #000,
    2px 1px 0px #000,
    2px 2px 0px #000,
    2px 3px 0px #000,
    3px -3px 0px #000,
    3px -2px 0px #000,
    3px -1px 0px #000,
    3px 0px 0px #000,
    3px 1px 0px #000,
    3px 2px 0px #000,
    3px 3px 0px #000
;
  }

  .title {
    top: 15%;
    font-size: 30px;
  }

  .timer {
    font-size: 45px;
    top: 63%;
    transform: translateY(-50%);
  }

  .timer > span:after {
    font-family: Consolas,Monaco,SFMono-Regular,Andale Mono,Liberation Mono,Ubuntu Mono,Menlo,monospace;
    width:0;
    animation-timing-function:step-end;
    animation-direction:normal;
    animation-play-state:running;
    animation-fill-mode:forwards;
    animation-iteration-count:infinite
  }

</style>
