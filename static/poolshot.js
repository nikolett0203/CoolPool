console.log("play_game.js loaded!");

let svg = document.querySelector('#pool-table svg');
console.log(svg)
svg.addEventListener('mousemove', drawline);
svg.addEventListener('mouseup', stopfollowingme);

let cueX, cueY;   // coordinates of cue ball
let mouseX, mouseY; // coordinates of mouse
let vX, vY;
let rect; // idek
let follow = false;    // mouse tracking
let line = null;    // cue line

function displaySVGs(svgFrames) {
    let currentFrameIndex = 0;

    let poolTable = document.getElementById("pool-table");
    // update svg with current shot frame and prepare next frame after 10 ms delay
    function displayNextFrame() {
        if (currentFrameIndex < svgFrames.length) {
            poolTable.innerHTML = svgFrames[currentFrameIndex];
            currentFrameIndex++; 
            // too fast if you don't set 10 millisecond delay on next frame
            setTimeout(displayNextFrame, 10);
        }
        else{
            // once all frames have been shown, request update on player stats
            updateStats();
        }
    }

    // start displaying the frames from the beginning
    displayNextFrame();

}

function shooot() {
    var to_server = new XMLHttpRequest();
    to_server.open("POST", "/shoot!", true);
    to_server.setRequestHeader("Content-Type", "application/json");

    to_server.onreadystatechange = function () {
        if (to_server.readyState === 4 && to_server.status === 200) {
            try {
                var svgFrames = JSON.parse(to_server.responseText);
                displaySVGs(svgFrames);
            } catch (e) {
                console.error("Error processing response:", e);
            }
        }
    };

    // Send velocity data as JSON
    to_server.send(JSON.stringify({ velX: vX, velY: vY }));
}

function followme(event) {
    follow = true;

    const cueBall = document.getElementById('cue'); // Get cue ball element

    cueX = parseFloat(cueBall.getAttribute('cx')); // Get cx attribute
    cueY = parseFloat(cueBall.getAttribute('cy')); // Get cy attribute

    rect = svg.getBoundingClientRect();

}

function convertSVG(evt, svgElem) {

    // creates SVGPoint object (data struct representing point in SVG's coord sys)
    let svgPoint = svgElem.createSVGPoint();
    // set x and y points according to brower's viewpoint coord system (NOT svg coord sys)
    svgPoint.x = evt.clientX;
    svgPoint.y = evt.clientY;
    // retrieves current transformation matrix of SVG element (all transformations applied to SVG)
    // reverse transformations to point matrix back to SVG coordinate system 
    let invertedMatrix = svgElem.getScreenCTM().inverse();
    // apply inverted CTM to SVG point to convert mouse viewport coords to SVG coords
    return svgPoint.matrixTransform(invertedMatrix);
}

function drawline(event) {

    if (follow){
        if (line) line.remove();

        const release = convertSVG(event, svg);

        line = document.createElementNS("http://www.w3.org/2000/svg", "line");

        line.setAttribute("x1", cueX);
        line.setAttribute("y1", cueY);
        line.setAttribute("x2", release.x);
        line.setAttribute("y2", release.y);
        line.setAttribute("stroke", "black");
        line.setAttribute("stroke-width", "7");

        svg.appendChild(line);

    }

}

function calculateSpeed(rawStart, rawShot) {

    const start = parseFloat(rawStart)
    const shot = parseFloat(rawShot)
    const rawSpeed = (start - shot) * 2.5;

    return Math.max(Math.min(rawSpeed, 10000), -10000);

}

function stopfollowingme() {

    follow = false;

    vX = 5;
    vY = 5;

    if (line) {

        vX = calculateSpeed(line.getAttribute('x1'), line.getAttribute('x2'))
        vY = calculateSpeed(line.getAttribute('y1'), line.getAttribute('y2'))

    }

    console.log(vX, vY)

    line.remove()
    shooot()

}

function updateStats() {

    svg = document.querySelector('#pool-table svg');
    svg.addEventListener('mousemove', drawline);
    svg.addEventListener('mouseup', stopfollowingme);

    var newReq = new XMLHttpRequest();
    newReq.open("POST", "/stats", true);
    newReq.setRequestHeader("Content-Type", "application/json");

    newReq.onreadystatechange = function() {
        if (newReq.readyState === 4 && newReq.status === 200) {
            try {
                var stats = JSON.parse(newReq.responseText);
                console.log("Received stats:", stats); // debug

                document.querySelector('.p1balls').textContent = stats.player1 + "'s remaining balls: " + stats.p1_count;
                document.querySelector('.p2balls').textContent = stats.player2 + "'s remaining balls: " + stats.p2_count;

                document.querySelector('.curr').textContent = "Current Player: " + stats.current;

                document.querySelector('.solids').textContent = "Solids: " + stats.lo_balls;
                document.querySelector('.stripes').textContent = "Stripes: " + stats.hi_balls;

                svg = document.querySelector('#pool-table svg');
                svg.addEventListener('mousemove', drawline);
                svg.addEventListener('mouseup', stopfollowingme);
            } catch (e) {
                console.error("JSON parsing error:", e);
            }
        }
    };

    newReq.send(JSON.stringify(null));
}
