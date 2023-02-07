<template>
  <v-stage
    ref="stage"
    :config="stageConfig"
    @dragend="onStageDragEnd"
  >
    <v-layer ref="layer">
      <template
        v-for="(person, personIndex) in persons"
        :key="'person-' + personIndex"
      >
        <v-group
          :config="{
            id: String(person.id),
            draggable: isSelectedPerson(person),
            x: person.x,
            y: person.y,
            scaleX: person.scale,
            scaleY: person.scale,
            name: 'person-group',
          }"
          @dragend="onPersonTransformed($event, person)"
          @touchend="onPersonTransformed($event, person)"
          @transformend="onPersonTransformed($event, person)"
        >
          <v-group
            :config="{
              clipFunc: clipFuncCircle,
            }"
          >
            <v-image
              :key="person.image"
              :config="{
                image: person.image,
                name: 'person-image',
              }"
            />
          </v-group>
          <v-group>
            <v-text
              :config="{
                x: 0,
                y: 320,
                width: 300,
                text: person.first_name + ' ' + person.last_name,
                align: 'center',
                fontSize: 36,
                name: 'person-name',
                fill: isSelectedPerson(person) ? 'red' : 'black',
              }"
            />
          </v-group>
        </v-group>
      </template>
    </v-layer>
  </v-stage>
  <!-- <v-container class="fill-height">

  </v-container> -->
</template>

<script>
  import Konva from 'konva';

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

  function clipFuncCircle (ctx) {
    ctx.arc(150, 150, 150, 0, Math.PI * 2, false);
  }

  // https://github.com/konvajs/konva/issues/1039
  const MOUSE_BUTTON_LEFT = 0;
  const MOUSE_BUTTON_MIDDLE = 1;
  Konva.dragButtons = [MOUSE_BUTTON_LEFT];

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

  function _httpRequest(method, url, payload = null) {
    const csrftoken = getCookie('csrftoken');
    const data = {
      method: method,
      headers: {
        'X-CSRFToken': csrftoken,
      },
      mode: 'cors',
    };
    if (payload !== null) {
      const formData = new FormData();
      for (const key of Object.keys(payload)) {
        const value = payload[key];
        formData.append(key, value);
      }
      data.body = formData;
    }
    return fetch(API_BASE_URL + url, data);
  }

  function httpGet(url) {
    return _httpRequest('GET', url);
  }

  function httpPost(url, payload) {
    return _httpRequest('POST', url, payload);
  }

  export default {
    data() {
      return {
        // Konva
        clipFuncCircle: clipFuncCircle,
        stageConfig: {
          width: window.innerWidth,
          height: window.innerHeight,
          draggable: false,
        },
        zoom: 1.0,
        transformer: {nodes: (_) => []},

        // cropperjs
        cropper: null,
        imageOriginalFilename: '',

        // Main fixed UI
        showDialog: false,
        firstName: '',
        lastName: '',

        // Backend data
        persons: [],
      };
    },
    computed: {
      dialogFormIsValid() {
        return (
          !!this.firstName && !this.firstName.trim() == '' &&
          !!this.lastName && !this.lastName.trim() == ''
        );
      },
      selectedNodes: {
        get() {
          if (!this.transformer) {
            return [];
          }
          return this.transformer.nodes();
        },
        set(nodes) {
          if (!this.transformer) {
            return;
          }
          this.transformer.nodes(nodes);
        },
      },
    },
    created() {
      this.fetchPersons().then((response) => {
        response.json().then((data) => {
          this.persons = data;
          this.loadPersonImages();
        });
      });
    },
    mounted() {
      // Apply remembered stage zoom and position.
      this.zoom = localStorage.getItem('stage.zoom') || 1.0;
      const stageX = (localStorage.getItem('stage.x') || 0)  / this.zoom;
      const stageY = (localStorage.getItem('stage.y') || 0)  / this.zoom;

      const stage = this.getStage();
      stage.scale({x: this.zoom , y: this.zoom});
      stage.x(stageX);
      stage.y(stageY);

      this.setupStageDragging();
      this.setupZoom();
      this.setupSelection();
    },
    methods: {
      onStageDragEnd() {
        this.rememberStageZoomAndPosition();
      },
      rememberStageZoomAndPosition() {
        const stage = this.getStage();
        localStorage.setItem('stage.zoom', this.zoom);
        localStorage.setItem('stage.x', stage.x() * this.zoom);
        localStorage.setItem('stage.y', stage.y() * this.zoom);
      },
      onImageSelected(event) {
        if (this.cropper) {
          this.cropper.destroy();
          this.cropper = null;
        }

        const imageFile = event.target.files[0];
        this.imageOriginalFilename = imageFile.name;

        const previewImage = this.$refs['image-cropper'];
        previewImage.src = URL.createObjectURL(imageFile);

        this.cropper = new Cropper(previewImage, {
          aspectRatio: 1,
          autoCropArea: 0.9,
        });
      },
      crop() {
        const vm = this;
        const canvas = vm.cropper.getCroppedCanvas({
          maxWidth: 2048,
          maxHeight: 2048,
          fillColor: 'black',
        });
        return new Promise((resolve, reject) => {
          canvas.toBlob(
            (blob) => {
              resolve(blob);
            },
            'image/png'
          );
        });
      },
      isSelectedPerson(person) {
        for (const node of this.selectedNodes) {
          if (node.attrs.id == person.id) {
            return true;
          }
        }
        return false;
      },
      resetDialog() {
        this.firstName = '';
        this.lastName = '';
      },
      closeDialog() {
        this.showDialog = false;
      },
      createPerson() {
        const vm = this;
        this.crop()
          .then((croppedAvatarBlob) => {
            const payload = {
              first_name: vm.firstName,
              last_name: vm.lastName,
              avatar: croppedAvatarBlob,
              avatar_filename: vm.imageOriginalFilename,
            };
            httpPost('/api/persons/create', payload)
              .then((response) => response.json())
              .then((person) => {
                function callback(person) {
                  vm.persons.push(person);
                }
                vm.loadPersonImage(person, callback);
                vm.resetDialog();
                vm.closeDialog();
                // TODO: Select person
              });
          });
      },
      onPersonTransformed(e, person) {
        const payload = {
          x: e.target.attrs.x,
          y: e.target.attrs.y,
          scale: e.target.attrs.scaleX,
        };
        httpPost('/api/persons/' + person.id, payload);
      },
      fetchPersons() {
        return httpGet('/api/persons/');
      },
      loadPersonImages() {
        for (let person of this.persons) {
          this.loadPersonImage(person);
        }
      },
      loadPersonImage(person, callback = null) {
        const image = new Image();
        if (!person.avatar) {
          return;
        }
        image.src = person.avatar;
        image.onload = () => {
          person.image = image;
          if (callback) {
            callback(person);
          }
        };
      },
      getStage() {
        return this.$refs.stage.getStage();
      },
      setupStageDragging() {
        const stage = this.getStage();
        stage.on('mousedown', (e) => {
          if (e.evt.button === MOUSE_BUTTON_MIDDLE) {
            stage.startDrag();
          }
        });
      },
      setupZoom() {
        const vm = this;
        const stage = this.getStage();
        const scaleBy = 1.12;

        stage.on('wheel', (e) => {
          // stop default scrolling
          e.evt.preventDefault();

          var oldScale = stage.scaleX();
          var pointer = stage.getPointerPosition();

          var mousePointTo = {
            x: (pointer.x - stage.x()) / oldScale,
            y: (pointer.y - stage.y()) / oldScale,
          };

          // how to scale? Zoom in? Or zoom out?
          let direction = e.evt.deltaY > 0 ? -1 : 1;

          // when we zoom on trackpad, e.evt.ctrlKey is true
          // in that case lets revert direction
          if (e.evt.ctrlKey) {
            direction = -direction;
          }

          vm.zoom  = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy;
          vm.rememberStageZoomAndPosition();
          stage.scale({x: vm.zoom , y: vm.zoom});

          var newPos = {
            x: pointer.x - mousePointTo.x * vm.zoom ,
            y: pointer.y - mousePointTo.y * vm.zoom ,
          };
          stage.position(newPos);
        });
      },
      setupSelection() {
        const vm = this;
        const stage = this.getStage();
        const layer = this.$refs.layer.getNode();

        const WIDTH_STEPS = [
          300, 450, 600, 750, 900, 1050, 1200
        ]
        const MIN_WIDTH = WIDTH_STEPS[0];
        const MAX_WIDTH = 2400;

        this.transformer = new Konva.Transformer({
          rotateEnabled: false,
          flipEnabled: false,
          resizeEnabled: true,
          // centeredScaling: true,
          enabledAnchors: [
            // 'top-left',
            // 'top-right',
            // 'bottom-left',
            'bottom-right',
          ],
          boundBoxFunc: function (oldBoundBox, newBoundBox) {
            // "boundBox" is an object with
            // x, y, width, height and rotation properties
            // transformer tool will try to fit nodes into that box

            if (
              Math.abs(newBoundBox.width) < MIN_WIDTH * vm.zoom ||
              Math.abs(newBoundBox.width) > MAX_WIDTH * vm.zoom
            ) {
              return oldBoundBox;
            }

            for (let i = 0; i < WIDTH_STEPS.length; i++) {
              let previousStep = MIN_WIDTH * vm.zoom;
              if (i > 0) {
                previousStep = WIDTH_STEPS[i - 1] * vm.zoom;
              }
              const step = WIDTH_STEPS[i] * vm.zoom;
              if (newBoundBox.width >= previousStep && newBoundBox.width <= step) {
                var bb = Object.assign({}, oldBoundBox);
                var ratio = newBoundBox.width / newBoundBox.height;
                var newWidth = (step - newBoundBox.width) <= (previousStep - newBoundBox.width) ? step : previousStep;
                bb.width = newWidth * ratio;
                bb.height = newWidth;
                return bb;
              }
            }

            return newBoundBox;
          },
        });
        layer.add(this.transformer);
        this.selectedNodes = [];

        // // add a new feature, lets add ability to draw selection rectangle
        // const selectionRectangle = new Konva.Rect({
        //   fill: 'rgba(0, 0, 255, 0.5)',
        //   visible: false,
        // });
        // layer.add(selectionRectangle);

        // let x1, y1, x2, y2;
        // stage.on('mousedown touchstart', (e) => {
        //   // do nothing if we mousedown on any shape
        //   if (e.target !== stage) {
        //     return;
        //   }
        //   e.evt.preventDefault();
        //   x1 = stage.getPointerPosition().x;
        //   y1 = stage.getPointerPosition().y;
        //   x2 = stage.getPointerPosition().x;
        //   y2 = stage.getPointerPosition().y;

        //   selectionRectangle.visible(true);
        //   selectionRectangle.width(0);
        //   selectionRectangle.height(0);
        // });

        // stage.on('mousemove touchmove', (e) => {
        //   // do nothing if we didn't start selection
        //   if (!selectionRectangle.visible()) {
        //     return;
        //   }
        //   e.evt.preventDefault();
        //   x2 = stage.getPointerPosition().x;
        //   y2 = stage.getPointerPosition().y;

        //   selectionRectangle.setAttrs({
        //     x: Math.min(x1, x2),
        //     y: Math.min(y1, y2),
        //     width: Math.abs(x2 - x1),
        //     height: Math.abs(y2 - y1),
        //   });
        // });

        // stage.on('mouseup touchend', (e) => {
        //   // do nothing if we didn't start selection
        //   if (!selectionRectangle.visible()) {
        //     return;
        //   }
        //   e.evt.preventDefault();
        //   // update visibility in timeout, so we can check it in click event
        //   setTimeout(() => {
        //     selectionRectangle.visible(false);
        //   });

        //   const shapes = stage.find('.person-group');
        //   const box = selectionRectangle.getClientRect();
        //   const selected = shapes.filter((shape) =>
        //     Konva.Util.haveIntersection(box, shape.getClientRect())
        //   );
        //   vm.selectedNodes = selected;
        // });

        // clicks should select/deselect shapes
        stage.on('click tap', function (e) {
          // // if we are selecting with rect, do nothing
          // if (selectionRectangle.visible()) {
          //   return;
          // }

          // if click on empty area - remove all selections
          if (e.target === stage) {
            vm.selectedNodes = [];
            return;
          }

          // Allow only specific elements as targets and get their
          // parent group as the actual thing we toggle the selection
          // on.
          let group = null;
          if (e.target.hasName('person-image') || e.target.hasName('person-name')) {
            group = e.target.getParent().getParent();
          }
          if (!group) {
            return;
          }

          // do we pressed shift or ctrl?
          const metaPressed = e.evt.shiftKey || e.evt.ctrlKey || e.evt.metaKey;
          const isSelected = vm.selectedNodes.indexOf(group) >= 0;

          if (!metaPressed && !isSelected) {
            // if no key pressed and the node is not selected
            // select just one
            vm.selectedNodes = [group];
          } else if (metaPressed && isSelected) {
            // if we pressed keys and node was selected
            // we need to remove it from selection:
            const nodes = vm.selectedNodes.slice(); // use slice to have new copy of array
            // remove node from array
            nodes.splice(nodes.indexOf(group), 1);
            vm.selectedNodes = nodes;
          } else if (metaPressed && !isSelected) {
            // add the node into selection
            const nodes = vm.selectedNodes.concat([group]);
            vm.selectedNodes = nodes;
          }
        });
      },
    }
  }
</script>

<style>
  /** cropperjs adaptations */

  /* Ensure the size of the image fit the container perfectly */
  .image-container img.image-cropper {
    display: block;
    /* This rule is very important, please don't ignore this */
    max-width: 100%;
  }
  /* https://github.com/fengyuanchen/cropper/issues/545 */
  .cropper-crop-box, .cropper-view-box {
    border-radius: 50%;
  }
  .cropper-view-box {
    box-shadow: 0 0 0 1px #39f;
    outline: 0;
  }
  .cropper-face {
    background-color: inherit !important;
  }
  /* .cropper-dashed, .cropper-point.point-se, .cropper-point.point-sw, .cropper-point.point-nw,   .cropper-point.point-ne, .cropper-line {
    display: none !important;
  } */
  .cropper-view-box {
    outline: inherit !important;
  }
</style>