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

    var windowWidth = window.innerWidth
    
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

    const likeButton = document.querySelector('#movie-like')
    const dislikeButton = document.querySelector('#movie-dislike')
    const bookmarkButton = document.querySelector('#movie-bookmark')

    if (likeButton) {
        likeButton.addEventListener('click', () => likePress())
        const likePress = () => {
            if (likeButton.classList.contains('active')) {
                likeButton.classList.remove('active')
                // Form submit goes here
            } else {
                if (dislikeButton.classList.contains('active')) {
                    dislikeButton.classList.remove('active')
                }
                likeButton.classList.add('active')
                // Form submit goes here
            }
        }
    }

    if (dislikeButton) {
        dislikeButton.addEventListener('click', () => dislikePress())
        const dislikePress = () => {
            if (dislikeButton.classList.contains('active')) {
                dislikeButton.classList.remove('active')
                // Form submit goes here
            } else {
                if (likeButton.classList.contains('active')) {
                    likeButton.classList.remove('active')
                }
                dislikeButton.classList.add('active')
                // Form submit goes here
            }
        }
    }

    if (bookmarkButton) {
        bookmarkButton.addEventListener('click', () => bookmarkPress())
        const bookmarkPress = () => {
            if (bookmarkButton.classList.contains('active')) {
                bookmarkButton.classList.remove('active')
                // Form submit goes here
            } else {
                bookmarkButton.classList.add('active')
                // Form submit goes here
            }
        }
    }

    const moviePoster = document.querySelector('#movie-poster-main')
    const backgroundElement = document.querySelector('#background')
    if (moviePoster) {
        if (moviePoster.getAttribute('src') != "") {
            backgroundElement.style.backgroundImage = "url('" + moviePoster.getAttribute('src') + "')"
            backgroundElement.classList.add('blured-background')
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
