def search_generator(artist_name: str, url: str, image: str):
    base = (
        ' <div class="col s12 m8 offset-m2 l6 offset-l3"> <div class="card-panel grey lighten-5 z-depth-1"> '
        '<div class="row valign-wrapper"> <div class="col s2"> <img src="{}" '
        'alt="" class="circle responsive-img"> </div><div class="col s10"> <a href="javascript:void(1)" style="font-size: 2em; color: black;" '
        'onclick="search_select(this);" onmouseover="this.style.color=\'#83CCC5\'" onmouseout="this.style.color=\'black\'">{}'
        '</a> </div><a href="{}" target="_blank" class="secondary-content">'
        '<i class="material-icons">open_in_new</i></a> '
        "</div></div></div>".format(image, artist_name, url)
    )
    return base


def carousel_generator(image_url: str, title: str):
    return '<a class="carousel-item" href="javascript:void(1)"><img src="{}" title="{}"></a>'.format(
        image_url, title
    )


no_image_default = [
    {"url": "image/red_square.png", "title": "Red Solid Square"},
    {"url": "image/green_square.png", "title": "Green Solid Square"},
    {"url": "image/blue_square.png", "title": "Blue Solid Square"},
]
