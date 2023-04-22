let map = null;
var center = {lat:43.0722,  lng:-89.4008}
var zoom = 16 
let locationUrl = "/locations" 
let highlightUrl = "/highlight" 
let highlighted = -1
let markers = [] // list of markers
let cafeterias = [] // list of cafeteria object


function createObject(data) {
    let id = data.id;
    let name = data.name;
    let location = { lat: parseFloat(data.coords_lat), lng: parseFloat(data.coords_lon)};
    let open_time = data.hours_open;
    let close_time = data.hours_closed;
    let status = data.status;
    let wait_times = data.wait_times
    let type = "Fast Food"
    if (data.type){
        type = data.type
    }
    let icon = "burger"
    if( type == "Dining"){
        icon = "utensils"
    }
    if (type == "Cafe"){
        icon = "coffee"
    }
    let crowd = "high"
    if (wait_times == "< 5 min") {
        crowd = 'low'
    }
    if (wait_times == "5 - 15 min"){
        crowd = 'medium'
    }
    if (status == "Closed") {
        crowd = 'closed'
    }
    return {
        id: id,
        name: name,
        status: status,
        wait_times: wait_times,
        type: type,
        icon: icon,
        open: open_time,
        close: close_time,
        crowd: crowd,
        location: location
    }
}



//向地图添加标记的函数
function addMarker(cafeterias) {
    for (const cafeteria of cafeterias) {
        const advancedMarkerView = new google.maps.marker.AdvancedMarkerView({
            map: null, //当map为null时，标记不会显示在地图上，我们将在其他函数中显示标记
            content: buildContent(cafeteria),
            position: cafeteria.location,
        });
        const element = advancedMarkerView.element;


        ["focus", "pointerenter"].forEach((event) => {
            element.addEventListener(event, () => {
                highlight(advancedMarkerView);
            });
        });
        ["blur", "pointerleave"].forEach((event) => {
            element.addEventListener(event, () => {
                unhighlight(advancedMarkerView);
            });
        });
        advancedMarkerView.addListener("click", (event) => {
            unhighlight(advancedMarkerView);
        });
        markers.push(advancedMarkerView)
    }
}


function highlight(markerView) {
    markerView.content.classList.add("highlight");
    markerView.element.style.zIndex = 1;
}

function unhighlight(markerView) {
    markerView.content.classList.remove("highlight");
    markerView.element.style.zIndex = "";
}

function buildContent(cafeteria) {
    const content = document.createElement("div");

    content.classList.add("property");
    content.innerHTML = `
        <div class="icon">
            <i aria-hidden="true" class="fa fa-solid fa-${cafeteria.icon} ${cafeteria.crowd}" title="${cafeteria.icon}"></i>
            <span class="fa-sr-only">${cafeteria.icon}</span>
        </div>
        <div class="details">
            <div class="name">${cafeteria.name}</div>
            <div class="wait">Wait Time: ${cafeteria.wait_times}</div>
            <div class="wait">Open Time: ${cafeteria.open}</div>
            <div class="wait">Close Time: ${cafeteria.close}</div>
            <div class="wait">Status: ${cafeteria.status}</div>
        </div>
        `;
    return content;
}

function setMarkerOn(marker) {
    marker.map = map;
}

function setMarkerOff(marker) {
    marker.map = null;
}
function filterCrowd() {
    let low = $("#low-check").prop("checked")
    let medium = $("#medium-check").prop("checked")
    let high = $("#high-check").prop("checked")
    let close = $("#close-check").prop("checked")
    for (let i = 0; i < markers.length; i++) {
        if(cafeterias[i].crowd === "high"){
            if (high) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
        else if(cafeterias[i].crowd === "low"){
            if (low) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
        else if(cafeterias[i].crowd === "medium"){
            if (medium) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
        else if(cafeterias[i].crowd === "closed"){
            if (close) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
    }
}

$("#high-check").change(filterCrowd)
$("#medium-check").change(filterCrowd)
$("#low-check").change(filterCrowd)
$("#close-check").change(filterCrowd)


function filterType() {
    let fast = $("#fast-check").prop("checked")
    let dining = $("#dining-check").prop("checked")
    let cafe = $("#cafe-check").prop("checked")
    for (let i = 0; i < markers.length; i++) {
        if(cafeterias[i].type === "Fast Food"){
            if (fast) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
        else if(cafeterias[i].type === "Dining"){
            if (dining) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
        else if(cafeterias[i].type === "Cafe"){
            if (cafe) {
                setMarkerOn(markers[i])
            }
            else{
                setMarkerOff(markers[i])
            }
        }
    }
}

$("#fast-check").change(filterType)
$("#dining-check").change(filterType)
$("#cafe-check").change(filterType)




const fetchLocation = async () => {
    const response = await fetch(locationUrl);
    const data = await response.json(); 
    for(let i = 0; i < data.length; i++){
        cafeterias.push(createObject(data[i]))
    }
}
const fetchHighlight = async () => {
    const response = await fetch(highlightUrl);
    const data = await response.json(); 
    highlighted = data[0]
}

async function initMap() {

    var myWrapper = $("#wrapper");
    $("#menu-toggle").click(function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
        myWrapper.one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function(e) {
            google.maps.event.trigger(map, 'resize');
        });
    });

    await fetchLocation()
    await fetchHighlight()
    addMarker(cafeterias)
    if(highlighted != -1){
        for (let i = 0; i < cafeterias.length; i++) {
            const current = cafeterias[i];
            if(current.id === highlighted){
                center = current.location
                zoom = 19
                highlight(markers[i])
            }
        }
    }

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: zoom,
        center: center,
        mapId: "4504f8b37365c3d0"
    });

    for (let i = 0; i < markers.length; i++) {
        setMarkerOn(markers[i]) 
    }
}

window.initMap = initMap;