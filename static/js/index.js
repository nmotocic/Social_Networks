/*
 * Welcome to your app's main JavaScript file!
 *
 * We recommend including the built version of this JavaScript file
 * (and its CSS file) in your base layout (base.html.twig).
 */

const rouletteWheel = document.getElementById('roulette-container');
if (rouletteWheel) {
    var padding = {top:0, right:20, bottom:0, left:20},
        w = 700 - padding.left - padding.right,
        h = 700 - padding.top  - padding.bottom,
        r = Math.min(w, h)/2,
        rotation = 0,
        oldrotation = 0,
        picked = 100000,
        oldpick = [],
        color = d3.scale.category20();//category20c()
        //randomNumbers = getRandomNumbers();

    var data = [
                {"label":"Dell LAPTOP",  "value":1,  "question":"What CSS property is used for specifying the area between the content and its border?"}, // padding
                {"label":"IMAC PRO",  "value":2,  "question":"What CSS property is used for changing the font?"}, //font-family
                {"label":"SUZUKI",  "value":3,  "question":"What CSS property is used for changing the color of text?"}, //color
                {"label":"HONDA",  "value":4,  "question":"What CSS property is used for changing the boldness of text?"}, //font-weight
                {"label":"FERRARI",  "value":5,  "question":"What CSS property is used for changing the size of text?"}, //font-size
                {"label":"APARTMENT",  "value":6,  "question":"What CSS property is used for changing the background color of a box?"}, //background-color
                {"label":"IPAD PRO",  "value":7,  "question":"Which word is used for specifying an HTML tag that is inside another tag?"}, //nesting
                {"label":"LAND",  "value":8,  "question":"Which side of the box is the third number in: margin:1px 1px 1px 1px; ?"}
    ];
    var svg = d3.select('#chart')
        .append("svg")
        .data([data])
        .attr("id", "chart-svg")
        .attr("width",  w + padding.left + padding.right)
        .attr("height", h + padding.top + padding.bottom);

    var postersContainer = svg.append("defs");
    var selectedMovies = document.getElementsByClassName("hidden-movie-data");
    for (var num = 0; num < selectedMovies.length; num++) {
        var posterPattern = postersContainer.append("pattern")
            .attr("id", "roulette-" + selectedMovies.item(num).id)
            .attr("patternUnits", "userSpaceOnUse")
            .attr("width", "596")
            .attr("height", "374")
            .attr("x", "-180")
            .attr("y", "-80")
            .attr("patternTransform", "rotate(" + (23 + (45 * num)) + ") scale(.75 .75)");
        var posterImages = posterPattern.append("image")
            .attr("href", selectedMovies.item(num).getElementsByTagName('img')[0].src)
            .attr("x", "0")
            .attr("y", "0")
            .attr("height", "545")
            .attr("width", "350");
    }

    var container = svg.append("g")
        .attr("class", "chartholder")
        .attr("transform", "translate(" + (w/2 + padding.left) + "," + (h/2 + padding.top) + ")");
    var vis = container
        .append("g");
        
    var pie = d3.layout.pie().sort(null).value(function(d){return 1;});
    // declare an arc generator function
    var arc = d3.svg.arc().outerRadius(r);
    // select paths, use arc generator to draw
    var arcs = vis.selectAll("g.slice")
        .data(pie)
        .enter()
        .append("g")
        .attr("class", "slice");
        
    arcs.append("path")
        .attr("fill", function(d, i){ return "url(#roulette-movie-" + i + ")"; })
        .attr("d", function (d) { return arc(d); });

    container.on("click", spin);
    function spin(d){
        
        container.on("click", null);

        var domSlices = document.getElementsByClassName("slice");
        for (var num = 0; num < domSlices.length; num++) {
            domSlices.item(num).classList.add('active');
        }

        //all slices have been seen, all done
        console.log("OldPick: " + oldpick.length, "Data length: " + data.length);
        if(oldpick.length == data.length){
            console.log("done");
            container.on("click", null);
            return;
        }
        var  ps       = 360/data.length,
            pieslice = Math.round(1440/data.length),
            rng      = Math.floor((Math.random() * 1440) + 360);
            
        rotation = (Math.round(rng / ps) * ps);
        
        picked = Math.round(data.length - (rotation % 360)/ps);
        picked = picked >= data.length ? (picked % data.length) : picked;
        if(oldpick.indexOf(picked) !== -1){
            d3.select(this).call(spin);
            return;
        } else {
            oldpick.push(picked);
        }
        rotation += 90 - Math.round(ps/2);
        vis.transition()
            .duration(3000)
            .attrTween("transform", rotTween)
            .each("end", function(){
                //mark question as seen
                // d3.select(".slice:nth-child(" + (picked + 1) + ") path")
                //     .attr("fill", "#111");
                //populate question
                // d3.select("#question h1")
                //     .text(data[picked].question);
                oldrotation = rotation;
        
                /* Get the result value from object "data" */
                console.log(data[picked].value)
                console.log(picked)

                var pickedMovie = document.getElementById('movie-' + picked);
                var chartVector = document.getElementById('chart-svg');
                if (pickedMovie) {
                    pickedMovie.classList.add('active');
                    chartVector.classList.add("inactive");
                }
        
                /* Comment the below line for restrict spin to sngle time */
                container.on("click", spin);
            });
    }

    //make arrow
    svg.append("g")
        .attr("transform", "translate(" + (w + padding.left + padding.right) + "," + ((h/2)+padding.top) + ")")
        .append("path")
        .attr("d", "M-" + (r*.15) + ",0L0," + (r*.05) + "L0,-" + (r*.05) + "Z")
        .style({"fill":"black"});

    //draw spin circle
    container.append("circle")
        .attr("cx", 0)
        .attr("cy", 0)
        .attr("r", 60)
        .attr("id", "spin-button");
        
    //spin text
    var text = container.append("text")
        .attr("x", 0)
        .attr("y", 10)
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(90)")
        .attr("id", "spin-button-text")
        .text("SPIN");


    function rotTween(to) {
    var i = d3.interpolate(oldrotation % 360, rotation);
    return function(t) {
        return "rotate(" + i(t) + ")";
    };
    }


    function getRandomNumbers(){
        var array = new Uint16Array(1000);
        var scale = d3.scale.linear().range([360, 1440]).domain([0, 100000]);
        if(window.hasOwnProperty("crypto") && typeof window.crypto.getRandomValues === "function"){
            window.crypto.getRandomValues(array);
            console.log("works");
        } else {
            //no support for crypto, get crappy random numbers
            for(var i=0; i < 1000; i++){
                array[i] = Math.floor(Math.random() * 100000) + 1;
            }
        }
        return array;
    }
}

function getMovieData () {
    var userMovieInput = document.getElementById('movie-title').value
    window.location = "http://localhost:5000/movie_api/" + userMovieInput
}

function getBookData () {
    var userBookInput = document.getElementById('book-title').value
    window.location = "http://localhost:5000/book_api/" + userBookInput
}

var graphDiv = document.getElementById("myChart");
const likeDisplay = document.getElementById("like-number");
if (likeDisplay) {
    var likeNum = likeDisplay.textContent
}
const dislikeDisplay = document.getElementById("dislike-number");
if (dislikeDisplay) {
    var dislikeNum = dislikeDisplay.textContent
}
const bookmarkDisplay = document.getElementById("bookmark-number");
if (bookmarkDisplay) {
    var bookmarkNum = bookmarkDisplay.textContent
}

if (graphDiv) {
    var graphContainer = graphDiv.getContext("2d");

    var chartData = {
        labels : ["Liked", "Disliked", "Bookmarked"],
        datasets : [{
            label: 'Legend',
            fill: true,
            lineTension: 0.1,
            backgroundColor: ["#18c939", "#c91818", "#0368ff"],
            borderColor: "#1f1f1f",
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderColor: "rgba(75,192,192,1)",
            pointBackgroundColor: "#fff",
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(75,192,192,1)",
            pointHoverBorderColor: "rgba(220,220,220,1)",
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data : [likeNum, dislikeNum, bookmarkNum]
        }]
    };
    
    var chartOptions = {
        legend: {
            display: false,
        }
    };
    
    if (graphContainer) {
        var myChart = new Chart(graphContainer, {
            type: 'doughnut',
            data: chartData,
            options: chartOptions
        });
    }
}

const weeklyGraphDiv = document.getElementById("weeklyChart");
const alltimeGraphDiv = document.getElementById("alltimeChart");
const likeWeeklyDisplay =  document.getElementById("likes-weekly-chart");
if (likeWeeklyDisplay) {
    var likeWeeklyNum = likeWeeklyDisplay.textContent
}
const dislikeWeeklyDisplay =  document.getElementById("dislikes-weekly-chart");
if (dislikeWeeklyDisplay) {
    var dislikeWeeklyNum = dislikeWeeklyDisplay.textContent
}
const likeAlltimeDisplay =  document.getElementById("likes-alltime-chart");
if (likeAlltimeDisplay) {
    var likeAlltimeNum = likeAlltimeDisplay.textContent
}
const dislikeAlltimeDisplay =  document.getElementById("dislikes-alltime-chart");
if (dislikeAlltimeDisplay) {
    var dislikeAlltimeNum = dislikeAlltimeDisplay.textContent
}

if (weeklyGraphDiv) {
    var graphContainer = weeklyGraphDiv.getContext("2d");

    var chartData = {
        labels : ["Liked", "Disliked"],
        datasets : [{
            label: 'Legend',
            fill: true,
            lineTension: 0.1,
            backgroundColor: ["#18c939", "#c91818"],
            borderColor: "#1f1f1f",
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderColor: "rgba(75,192,192,1)",
            pointBackgroundColor: "#fff",
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(75,192,192,1)",
            pointHoverBorderColor: "rgba(220,220,220,1)",
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data : [likeWeeklyNum, dislikeWeeklyNum]
        }]
    };
    
    var chartOptions = {
        legend: {
            display: false,
        },
        title: {
            display: true,
            text: 'Weekly Ratings'
        }
    };
    
    if (graphContainer) {
        var myChart = new Chart(graphContainer, {
            type: 'doughnut',
            data: chartData,
            options: chartOptions
        });
    }
}

if (alltimeGraphDiv) {
    var graphContainer = alltimeGraphDiv.getContext("2d");

    var chartData = {
        labels : ["Liked", "Disliked"],
        datasets : [{
            label: 'Legend',
            fill: true,
            lineTension: 0.1,
            backgroundColor: ["#18c939", "#c91818"],
            borderColor: "#1f1f1f",
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderColor: "rgba(75,192,192,1)",
            pointBackgroundColor: "#fff",
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(75,192,192,1)",
            pointHoverBorderColor: "rgba(220,220,220,1)",
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data : [likeAlltimeNum, dislikeAlltimeNum]
        }]
    };
    
    var chartOptions = {
        legend: {
            display: false,
        },
        title: {
            display: true,
            text: 'All Time Ratings'
        }
    };
    
    if (graphContainer) {
        var myChart = new Chart(graphContainer, {
            type: 'doughnut',
            data: chartData,
            options: chartOptions
        });
    }
}

;(() => {
    const menu = document.querySelector('#nav')
    const menuToggleButton = document.querySelector('#toggle-nav')
    const body = document.querySelector('body')

    const hideForLogin = document.getElementById("login-page")
    const userInfo = document.getElementById("user-info")
    const baseLocation = "http://localhost:5000/"

    const logoElement = document.querySelector('#logo-image')
    const logoImageLargeSrc = "/static/images/MovieRouletteLogo.png"
    const logoImagesmallSrc = "/static/images/MovieRouletteLogoSmall.png"

    var windowWidth = window.innerWidth

    if(hideForLogin) {
        menu.style.display = "none";
        userInfo.style.display = "none";
        menuToggleButton.style.display = "none";
    }
    
    if (windowWidth <= 980) {
        logoElement.setAttribute("src", logoImagesmallSrc)
    } else {
        logoElement.setAttribute("src", logoImageLargeSrc)
    }

    window.addEventListener('resize', function(event) {
        var width = window.innerWidth
    
        if (width <= 980) {
            logoElement.setAttribute("src", logoImagesmallSrc)
        } else {
            logoElement.setAttribute("src", logoImageLargeSrc)
        }
    })

    if (menuToggleButton) {
        menuToggleButton.addEventListener('click', () => menuShow())
        const menuShow = () => {
            if (menu.classList.contains('active')) {
                menu.classList.remove('active')
                menuToggleButton.classList.remove('active')
                menuToggleButton.style.backgroundImage = 'url("/static/images/bars-solid.svg")'
                body.classList.remove('nav-active')
            } else {
                menu.classList.add('active')
                menuToggleButton.classList.add('active')
                menuToggleButton.style.backgroundImage = 'url("/static/images/arrow-left-solid.svg")'
                body.classList.add('nav-active')
            }
        }
    }

    const likeButton = document.querySelector('#movie-like')
    const dislikeButton = document.querySelector('#movie-dislike')
    const bookmarkButton = document.querySelector('#movie-bookmark')
    const urlSegments = window.location.href.split('/')
    if (urlSegments) {
        const movieID = urlSegments[urlSegments.length - 1]
        if (movieID) {
            if (likeButton) {
                likeButton.addEventListener('click', () => likePress())
                const likePress = () => {
                    if (likeButton.classList.contains('active')) {
                        likeButton.classList.remove('active')
                    } else {
                        if (dislikeButton.classList.contains('active')) {
                            dislikeButton.classList.remove('active')
                        }
                        likeButton.classList.add('active')
                    }
                    // console.log(baseLocation + 'movie/' + movieID + '/like')
                    window.location.replace(baseLocation + 'movie/' + movieID + '/like')
                }
            }
        
            if (dislikeButton) {
                dislikeButton.addEventListener('click', () => dislikePress())
                const dislikePress = () => {
                    if (dislikeButton.classList.contains('active')) {
                        dislikeButton.classList.remove('active')
                    } else {
                        if (likeButton.classList.contains('active')) {
                            likeButton.classList.remove('active')
                        }
                        dislikeButton.classList.add('active')
                    }
                    // console.log(baseLocation + 'movie/' + movieID + '/dislike')
                    window.location.replace(baseLocation + 'movie/' + movieID + '/dislike')
                }
            }
        
            if (bookmarkButton) {
                bookmarkButton.addEventListener('click', () => bookmarkPress())
                const bookmarkPress = () => {
                    if (bookmarkButton.classList.contains('active')) {
                        bookmarkButton.classList.remove('active')
                    } else {
                        bookmarkButton.classList.add('active')
                    }
                    // console.log(baseLocation + 'movie/' + movieID + '/favourite')
                    window.location.replace(baseLocation + 'movie/' + movieID + '/favorite')
                }
            }
        }
    }

    const moviePoster = document.querySelector('#movie-poster-main')
    const backgroundElement = document.querySelector('#background')
    if (moviePoster) {
        if (moviePoster.getAttribute('src') != "") {
            if (backgroundElement) {
                backgroundElement.style.backgroundImage = "url('" + moviePoster.getAttribute('src') + "')"
                backgroundElement.classList.add('blured-background')
            }
        }
    }

    const toggleSettingsButton = document.querySelector('#toggle-settings')
    const settingContainer = document.querySelector('#roulette-settings')
    if (toggleSettingsButton) {
        if (settingContainer) {
            toggleSettingsButton.addEventListener('click', () => toggleSettingsDisplay())
            const toggleSettingsDisplay = () => {
                if (settingContainer.classList.contains('active')) {
                    settingContainer.classList.remove('active')
                } else {
                    settingContainer.classList.add('active')
                }
            }
        }
    }

    const srchBtn = document.querySelector("#srch-btn")
    var srchTextArea = document.getElementById("srch-text-area")
    if (srchBtn) {
        srchBtn.addEventListener('click', () => searchMovies())
        const searchMovies = () => {
            if (srchTextArea.value != "") {
                window.location.replace( baseLocation + 'srch/' + srchTextArea.value )
            }
        }
    }

})()
