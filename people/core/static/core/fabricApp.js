const { ObjectFit } = FabricJSObjectFit.setup(fabric);

// https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function httpPost(url, payload) {
  const csrftoken = getCookie('csrftoken');
  const formData = new FormData();
  for (const key of Object.keys(payload)) {
    const value = payload[key];
    formData.append(key, value);
  }
  return fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken},
    mode: 'same-origin',
    body: formData,
  });
}

var canvas = new fabric.Canvas("canvas", {
  width: window.innerWidth,
  height: window.innerHeight,
  uniformScaling: true,
  uniscaleKey: 'null',
});

function setDefaultControls(obj) {
  // obj.cornerStyle = "circle";
  // obj.cornerSize = 16;
  // obj.transparentCorners = false;
  // obj.centeredScaling = true;
  // obj.centeredRotation = true;
  for (let controlName of ['tl', 'tr', 'br', 'bl', 'ml', 'mt', 'mr', 'mb', 'mtr']) {
    obj.setControlVisible(controlName, false);
  }
}

setDefaultControls(fabric.Object.prototype);

// Zoom & pan (Alt + drag), see: http://fabricjs.com/fabric-intro-part-5
canvas.on("mouse:down", function (opt) {
  var evt = opt.e;
  if (evt.altKey === true) {
    this.isDragging = true;
    this.selection = false;
    this.lastPosX = evt.clientX;
    this.lastPosY = evt.clientY;
  }
});
canvas.on("mouse:move", function (opt) {
  if (this.isDragging) {
    var e = opt.e;
    var vpt = this.viewportTransform;
    vpt[4] += e.clientX - this.lastPosX;
    vpt[5] += e.clientY - this.lastPosY;
    this.requestRenderAll();
    this.lastPosX = e.clientX;
    this.lastPosY = e.clientY;
  }
});
canvas.on("mouse:up", function (opt) {
  // on mouse up we want to recalculate new interaction
  // for all objects, so we call setViewportTransform
  this.setViewportTransform(this.viewportTransform);
  this.isDragging = false;
  this.selection = true;
});
canvas.on("mouse:wheel", function (opt) {
  var delta = opt.e.deltaY;
  var zoom = canvas.getZoom();
  zoom *= 0.999 ** delta;
  if (zoom > 20) zoom = 20;
  if (zoom < 0.01) zoom = 0.01;
  canvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom);
  opt.e.preventDefault();
  opt.e.stopPropagation();
});

function addPerson(
  personId, firstName, lastName, avatarImageUrl, x, y, angle, scale
) {
  const cachebuster = '?' + (Math.random() + 1).toString(36).substring(7);
  const fixedWidth = 240;

  fabric.Image.fromURL(avatarImageUrl + cachebuster, function (img) {
    // Simulate css's 'object-fit' via FabricJSObjectFit.
    const imageContainer = new ObjectFit(img, {
      width: fixedWidth,
      height: fixedWidth,
      mode: "cover",
    });
    // imageContainer.set("shadow", {
    //   blur: 16, offsetX: 4, offsetY: 4, color: "rgba(0,0,0,0.25)"
    // });
    imageContainer.set({
      clipPath: new fabric.Circle({
        radius: fixedWidth / 2,
        originX: "center",
        originY: "center",
      })
    });

    var text = new fabric.Text(firstName + ' ' + lastName, {
      textAlign: 'center',
      top: imageContainer.top + imageContainer.height + 12,
      fill: "black",
      fontFamily: "Arial, sans-serif",
      fontSize: 36
    });
    text.left = (imageContainer.width - text.width) / 2;

    var group = new fabric.Group([imageContainer, text]);
    group.left = x;
    group.top = y;
    // group.angle = angle;
    group.scaleX = scale;
    group.scaleY = scale;
    group.minScaleLimit = 0.5;
    group.lockScalingFlip = true;
    group.lockRotation = true;
    group.lockScalingX = true;
    group.lockScalingY = true;

    canvas.add(group);

    // Setup events.
    if (personId) {
      group.on("modified", function (opt) {
        const obj = opt.target;
        const payload = {
          x: obj.left,
          y: obj.top,
          angle: obj.angle,
          scale: obj.scaleX,
        };
        httpPost('/persons/' + personId, payload);
      });
    }
  });
}
