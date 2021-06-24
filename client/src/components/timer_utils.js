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


const padNumber = (num) => String(num).padStart(2, '0');

function buildSvg(
  time
) {
  let ret = [];

  const endDate = new Date(time);
  const end = endDate.getTime();
  const now = new Date().getTime();

  let seconds = (end - now) / 1000;
  const allSecondsLeft = Math.round(seconds);

  const hoursLeft = Math.floor(allSecondsLeft / 3600);
  seconds = seconds - hoursLeft * 3600;
  const hoursDelay = seconds;

  const minutesLeft = Math.floor(seconds / 60);
  seconds = seconds - minutesLeft * 60;
  const secondsLeft = Math.round(seconds);
  const minutesDelay = secondsLeft;

  ret.push(`.seconds::after { content: "${secondsLeft}"; animation-name: countdown-seconds; animation-duration: 60s; }`);
  ret.push(`.minutes::after { content: "${minutesLeft}"; animation-name: countdown-minutes; animation-duration: 3600s; animation-delay: ${minutesDelay}s }`);
  ret.push(`.hours::after { content: "${hoursLeft}"; animation-name: countdown-hours; animation-duration: 86400s; animation-delay: ${hoursDelay}s }`);
  ret.push(`.timer { opacity: 100%; animation-name: timer-disappear; animation-duration: 1s; animation-timing-function:step-end;animation-direction: normal; animation-play-state: running; animation-fill-mode: forwards; animation-delay: ${allSecondsLeft - 1}s }`);
  ret.push(`.finish { opacity: 0%; animation-name: finish-appear; animation-duration: 1s; animation-timing-function:step-end; animation-direction: normal; animation-play-state: running; animation-fill-mode: forwards; animation-delay: ${allSecondsLeft - 1}s }`);

  ret.push(createKeyframes(secondsLeft - 1, 60, 'seconds'));
  ret.push(createKeyframes(minutesLeft - 1, 60, 'minutes'));
  ret.push(createKeyframes(hoursLeft - 1, 24, 'hours'));

  return ret
}

function formatTime(date) {
  return `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}-${date.getUTCDate()} ${padNumber(date.getUTCHours())}:${padNumber(date.getUTCMinutes())}:${padNumber(date.getUTCSeconds())} UTC`;
}

function createKeyframes(start, steps, name) {
  let result = `@keyframes countdown-${name} {`;

  for (let i = 0; i < steps; i++) {
    result += `${((100 / steps) * i).toFixed(2)}%{`;
    result += `content: "${start - i >= 0 ? start - i : steps + start - i}"`;
    result += '}';
  }

  result += '100%{';
  result += `content:"${start - steps + 1 >= 0 ? start - steps + 1 : start + 1}"`;
  result += '}';

  result += '}';
  return result;
}

export {
    buildSvg
}