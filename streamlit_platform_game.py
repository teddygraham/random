import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simple Platformer")

st.title("Simple Pixel Platformer")

html_code = """
<style>
canvas { background: #000; display: block; margin: 0 auto; }
body { margin: 0; overflow: hidden; }
</style>
<canvas id='gameCanvas' width='800' height='400'></canvas>
<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let keys = {};

document.addEventListener('keydown', (e) => { keys[e.code] = true; });
document.addEventListener('keyup', (e) => { keys[e.code] = false; });

const player = { x: 50, y: 0, w: 20, h: 20, vx: 0, vy: 0, onGround: false };
const gravity = 0.5;
const friction = 0.8;
const jumpStrength = -10;
const platforms = [
    {x:0, y:380, w:800, h:20},
    {x:200, y:300, w:120, h:10},
    {x:400, y:250, w:120, h:10}
];

function update() {
    if(keys['ArrowLeft']) { player.vx = -3; }
    if(keys['ArrowRight']) { player.vx = 3; }
    if(keys['Space'] && player.onGround) { player.vy = jumpStrength; player.onGround = false; }

    player.vy += gravity;
    player.x += player.vx;
    player.y += player.vy;

    player.onGround = false;
    for(let p of platforms) {
        if(player.x < p.x + p.w && player.x + player.w > p.x &&
           player.y + player.h < p.y + 1 && player.y + player.h + player.vy >= p.y) {
            player.y = p.y - player.h;
            player.vy = 0;
            player.onGround = true;
        }
    }
    player.vx *= friction;
}

function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = 'yellow';
    ctx.fillRect(player.x, player.y, player.w, player.h);
    ctx.fillStyle = 'white';
    for(let p of platforms) {
        ctx.fillRect(p.x, p.y, p.w, p.h);
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}
loop();
</script>
"""

components.html(html_code, height=410)

