(function ($) {
    $(function () {

        $('.sidenav').sidenav();
        $('.parallax').parallax();

    }); // end of document ready
})(jQuery); // end of jQuery name space

let selectedArtist = "";

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

$("#example_pictures").carousel();
$('.materialboxed').materialbox();


let search = function () {
    let bar = document.getElementById("search_bar");
    let results_container = document.getElementById("search_results");
    let value = bar.value;
    if (value === "") {
        alert("Search Empty");
        return
    }

    fetch(
        "api/search", {
            method: "POST",
            body: value
        }
    ).then(function (response) {
        response.text().then(function (text) {
            results_container.innerHTML = text;
            setTimeout(function () {
                $('html,body').animate({
                    scrollTop: $("#search_container").offset().top - 15
                }, 1000);

            }, 250);
        })
    })

};

let search_select = function (context) {
    let artist = context.innerText;
    let search_results = document.getElementById("search_results");
    let children = search_results.children;
    for (let a in children) {
        if (typeof children[a] === "object") {
            if (!children[a].contains(context)) {
                children[a].style = "display: none;"
            }
        }
    }
    document.getElementById("search_container").style = "display: none;";
    document.getElementById("search_back").style = "";
    selectedArtist = artist;
    start_carousel(artist)
};

let search_back = function () {
    let search_results = document.getElementById("search_results");
    let children = search_results.children;
    for (let a in children) {
        try {
            children[a].style = ""

        } catch (e) {
        }

    }
    document.getElementById("search_container").style = "";
    document.getElementById("search_back").style = "display: none;";
    document.getElementById("image_selection_container").style = "display:none;"
};

let start_carousel = function (artist_name) {
    let carousel = document.getElementById("carousel");
    document.getElementById("image_selection_container").style = "";
    fetch("api/album_art", {
        method: "POST",
        body: artist_name,
    }).then(response => {

        response.text().then(body => {
            carousel.innerHTML = body;
            $('.carousel').carousel();
            $('html,body').animate({
                scrollTop: $("#image_selection_container").offset().top
            }, 1000);
        })
    })
};

let step = 0;

let update_frontend = function (json) {
    let b1 = document.getElementById("progress_b1");
    let b2 = document.getElementById("progress_b2");
    let b3 = document.getElementById("progress_b3");
    let bar = document.getElementById("progress");
    let text = document.getElementById("progress_text");

    let dark = "color: #FFF";
    let light = "color: rgba(255, 255, 255, 0.7)";

    if (step === 0) {
        bar.setAttribute("class", "determinate");
        bar.setAttribute("style", "width: 0%;");
        step = 1;
    }

    if (step === 1) {
        if (json["LYRICS_GATHERING_DONE"] === "TRUE") {
            b1.setAttribute("style", light);
            b2.setAttribute("style", dark);
            b3.setAttribute("style", light);

            bar.setAttribute("class", "indeterminate");
            text.setAttribute("hidden", "");

            step = 2;
        } else {
            let _step = json["LYRICS_GATHERING_STEPS"];
            let max = json["LYRICS_GATHERING_ALL"];

            let perc = _step / max;
            perc = perc * 100;
            perc = Math.round(perc);

            if (isNaN(perc)) {
                perc = 0
            }

            bar.setAttribute("style", "width: " + perc + "%;");
            text.innerText = perc + "%";
        }
    }

    if (step === 2) {
        if (json["DONE"] === "TRUE") {
            let url = json["URL"];
            let ip = document.getElementById("image_preview");
            ip.src = url;
            let image_box = document.getElementById("image_box");
            let image_open = document.getElementById("image_open");
            let progress_c = document.getElementById("progress_c");
            let pat = document.getElementById("patience_text");
            pat.innerText = "Done!";
            progress_c.style = "display:none;";
            image_open.href = url;
            image_box.style = "";
            let image_download = document.getElementById("image_download");
            let base = "api/download?url=";
            let enc = btoa(url);
            image_download.href = base + enc
        }
    }

};

let update_check = function (job_id) {

    fetch("api/image_status", {
        method: 'POST',
        body: job_id
    }).then(res => {
        res.text().then(text => {
            let a = JSON.parse(text);
            console.log(a);
            update_frontend(a);
            if (a["DONE"] === "FALSE") {
                setTimeout(function () {
                    update_check(job_id)
                }, 3000)
            }
        })
    })
};

let submit = function () {
    let url = "";
    let carousel = document.getElementById("carousel");
    let children = carousel.children;
    for (let child in children) {
        if (typeof children[child] === "object") {
            if (children[child].classList.contains("active")) {
                url = children[child].children[0].src;
            }
        }
    }
    let d = {
        "artist": selectedArtist,
        "image_url": url,
        "predefined_image": true
    };
    let _doc = JSON.stringify(d);
    document.getElementById("progress_container").style = "";
    document.getElementById("getting_started").setAttribute("hidden", "true");
    document.getElementById("patience").style = "min-height: auto;";
    document.getElementById("select_cont").style = "display:none;";
    fetch("api/generate_image", {
        method: "POST",
        body: _doc,
    }).then(response => {
        response.text().then(job_id => {
            update_check(job_id);
        })
    })
};