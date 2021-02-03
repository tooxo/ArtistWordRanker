(function ($) {
    $(function () {

        $('.sidenav').sidenav();
        $('.parallax').parallax();

    }); // end of document ready
})(jQuery); // end of jQuery name space

let selectedArtist = "";
let selectedFile = null;

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
    let artist_id = context.getAttribute("spotify_id");
    let search_results = document.getElementById("search_results");
    let children = search_results.children;
    for (let a of children) {
        if (typeof a === "object") {
            if (!a.contains(context)) {
                a.style = "display: none;"
            }
        }
    }
    document.getElementById("search_container").style = "display: none;";
    document.getElementById("search_back").style = "";
    selectedArtist = artist_id;
    start_carousel(artist_id)
};

let search_back = function () {
    let search_results = document.getElementById("search_results");
    let children = search_results.children;
    for (let a of children) {
        try {
            a.style = ""

        } catch (e) {
        }

    }
    document.getElementById("search_container").style = "";
    document.getElementById("search_back").style = "display: none;";
    document.getElementById("image_selection_container").style = "display:none;"
};

let start_carousel = function (artist_id) {
    let carousel = document.getElementById("carousel");
    document.getElementById("image_selection_container").style = "";
    fetch("api/album_art", {
        method: "POST",
        body: artist_id,
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
            // ip.src = url;
            let image_download = document.getElementById("image_download");
            let image_box = document.getElementById("image_box");
            let image_open = document.getElementById("image_open");
            let progress_c = document.getElementById("progress_c");
            let pat = document.getElementById("patience_text");
            let vector_download = document.getElementById("vector_download");

            fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`)
                .then(response => {
                    response.json().then(
                        (text) => {
                            ip.src = "data:image/svg+xml;charset=utf-8," + text["contents"];
                        }
                    )
                });

            ip.onload = (event) => {
                let canvas = document.createElement('canvas');
                let context = canvas.getContext('2d');
                let regex = /<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" width="([\d.]+)" height="([\d.]+)">/;
                let result = regex.exec(ip.src);
                canvas.width = Number.parseInt(result[1]);
                canvas.height = Number.parseInt(result[2]);
                context.drawImage(ip, 0, 0);
                // let myData = context.getImageData(0, 0, 1500, 1500);
                // let blob = new Blob([myData], {type: "image/jpeg"});
                image_download.download = "image.png"
                // image_download.href = window.URL.createObjectURL(blob);
                image_download.href = canvas.toDataURL();
            }

            pat.innerText = "Done!";
            progress_c.style = "display:none;";
            image_open.href = url;
            image_box.style = "";
            let base = "api/download?url=";
            let enc = btoa(url);
            vector_download.href = base + enc + "&mime=" + btoa("image/svg+xml") + "&ext=svg"
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

let submit = async function () {
    let url = "";
    if (selectedFile != null) {

        const toBase64 = file => new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = error => reject(error);
        });
        url = await toBase64(selectedFile)
    } else {
        let carousel = document.getElementById("carousel");
        let children = carousel.children;
        for (let child of children) {
            if (typeof child === "object") {
                if (child.classList.contains("active")) {
                    url = child.children[0].src;
                }
            }
        }
    }
    let d = {
        "artist": selectedArtist,
        "image_url": url,
        "predefined_image": selectedFile == null
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

let fileUpload = function () {
    let input = document.getElementById("fileInput");
    input.click();
}

let fileChanged = function () {
    let files = document.getElementById("fileInput").files;
    if (files === undefined) return;
    if (!["image/jpeg", "image/png"].includes(files[0].type)) return;
    if (files[0].size > 2000000) return;
    selectedFile = files[0]
    document.getElementsByClassName("fileUpload")[0].innerText = selectedFile.name;
    for (let image of document.getElementById("carousel").querySelectorAll("img")) {
        image.setAttribute("style", "filter:grayscale(100%);");
    }
    document.getElementById("clearButton").setAttribute("style", "");
}

let fileClear = function () {
    selectedFile = null;
    for (let image of document.getElementById("carousel").querySelectorAll("img")) {
        image.setAttribute("style", "");
    }
    document.getElementsByClassName("fileUpload")[0].innerText = "upload your own file";
    document.getElementById("clearButton").setAttribute("style", "display:none");
}