/*
 * Welcome to your app's main JavaScript file!
 *
 * We recommend including the built version of this JavaScript file
 * (and its CSS file) in your base layout (base.html.twig).
 */

function getMovieData () {
    var userMovieInput = document.getElementById('movie-title').value
    window.location = "http://localhost:5000/movie_api/" + userMovieInput
}

function getBookData () {
    var userBookInput = document.getElementById('book-title').value
    window.location = "http://localhost:5000/book_api/" + userBookInput
}

;(() => {
    const menu = document.querySelector('#nav')
    const body = document.querySelector('body')
    const logoElement = document.querySelector('#logo-image')
    const logoImageLargeSrc = "/static/images/MovieRouletteLogo.png"
    const logoImagesmallSrc = "/static/images/MovieRouletteLogoSmall.png"

    window.addEventListener('resize', function(event) {
        var width = window.innerWidth
    
        if (width <= 980) {
            logoElement.setAttribute("src", logoImagesmallSrc)
        } else {
            logoElement.setAttribute("src", logoImageLargeSrc)
        }
    })

    const menuToggleButton = document.querySelector('#toggle-nav')
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

    const uploadFileButton = document.querySelector('#upload-file-button')
    if (uploadFileButton) {
        uploadFileButton.addEventListener('click', (event) => uploadImage())
        const uploadImage = () => {
            document.getElementById("file-input").click()
        }
    }
})()
