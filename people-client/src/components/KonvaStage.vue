<template>
  <div>
    <!-- Konva JS Stage (canvas) -->
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
                :key="person.avatar"
                :config="{
                  image: person.image,
                  name: 'person-image',
                  opacity: !!person.date_of_death ? 0.5 : 1.0,
                }"
              />
            </v-group>
            <v-group>
              <v-text
                :config="{
                  x: 0,
                  y: 320,
                  width: 300,
                  text: person.name,
                  align: 'center',
                  fontSize: 36,
                  name: 'person-name',
                  fill: isSelectedPerson(person) ? 'red' : 'black',
                  opacity: !!person.date_of_death ? 0.5 : 1.0,
                }"
              />
            </v-group>
          </v-group>
        </template>
      </v-layer>
    </v-stage>
    <!-- Other UI Stuff -->
    <v-scale-transition>
      <div
        v-show="selectedNodes.length == 1 && !!enableContextMenuForPerson"
      >
        <v-menu
          v-if="groupContextMenuLeft != -1 && groupContextMenuTop != -1"
          v-model="enableContextMenu"
          style="
            position: absolute;
            z-index: 99999;
          "
          :style="{
            left: groupContextMenuLeft,
            top: groupContextMenuTop,
          }"
        >
          <v-list v-model="menu">
            <v-list-item
              v-if="!!enableContextMenuForPerson"
              @click="store.setEditedPerson(enableContextMenuForPerson)"
            >
              <v-avatar>
                <v-icon icon="mdi-pencil"></v-icon>
              </v-avatar>
              Edit <strong class="nowrap">{{ enableContextMenuForPerson.name }}</strong>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </v-scale-transition>
  </div>
</template>

<script>
  import Konva from 'konva';

  import { useAppStore } from '@/store/app';
  const store = useAppStore();

  import { httpGet, httpPost } from '@/httpClient.js';

  function clipFuncCircle (ctx) {
    ctx.arc(150, 150, 150, 0, Math.PI * 2, false);
  }

  // https://github.com/konvajs/konva/issues/1039
  const MOUSE_BUTTON_LEFT = 0;
  const MOUSE_BUTTON_MIDDLE = 1;
  Konva.dragButtons = [MOUSE_BUTTON_LEFT];

  const initialZoom = 0.5;

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
        zoom: initialZoom,
        transformer: {nodes: (_) => []},
        activeSelectionRectangle: false,

        enableContextMenu: true,
        enableContextMenuForPerson: null,
        menu: false,
        groupContextMenuTop: -1,
        groupContextMenuLeft: -1,

        store: store,

        // cropperjs
        cropper: null,
        imageOriginalFilename: '',
      };
    },
    computed: {
      persons() {
        return this.store.persons;
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
    watch: {
      'selectedNodes': function() {
        if (!this.selectedNodes || this.selectedNodes.length == 0) {
          this.resetContextMenu();
        }
      },
    },
    created() {
      const vm = this;
      this.store.$onAction(function(opts) {
        if (opts.name == 'addPerson' || opts.name == 'updatePerson') {
          const person = opts.args[0];
          const doSelect = opts.name == 'addPerson';
          const callback = doSelect ? () => vm.$nextTick(() => vm.selectPerson(person.id)) : null;
          vm.loadPersonImage(person, callback);
        }
      });

      this.fetchPersons().then((response) => {
        response.json().then((persons) => {
          this.store.setPersons(persons);
          this.loadPersonImages();
        });
      });
    },
    mounted() {
      // Apply remembered stage zoom and position.
      this.zoom = localStorage.getItem('stage.zoom') || initialZoom;
      const stageX = (localStorage.getItem('stage.x') || 0)  / this.zoom;
      const stageY = (localStorage.getItem('stage.y') || 0)  / this.zoom;

      const stage = this.getStage();
      stage.scale({x: this.zoom , y: this.zoom});
      stage.x(stageX);
      stage.y(stageY);

      this.setupStageDragging();
      this.setupZoom();
      this.setupSelection();
      this.setupGroupContextMenu();
    },
    methods: {
      resetContextMenu() {
        this.enableContextMenu = false;
        this.enableContextMenuForPerson = null;
      },
      resetSelectedNodes() {
        this.selectedNodes = [];
      },
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
      onPersonTransformed(e, person) {
        const payload = {
          x: e.target.attrs.x,
          y: e.target.attrs.y,
          scale: e.target.attrs.scaleX,
        };
        httpPost('/api/persons/' + person.id + '/transforms', payload);
      },
      onPersonSelected(e, person) {
        this.store.setEditedPerson(person);
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
      setupGroupContextMenu() {
        const vm = this;
        const stage = this.getStage();
        stage.on('contextmenu', function (e) {
          if (e.target === stage) {
            return;
          }

          // Prevent default behavior when something specific was targetted..
          e.evt.preventDefault();

          let group;
          if (e.target.hasName('person-image') || e.target.hasName('person-name')) {
            group = e.target.getParent().getParent();
          }
          if (group) {
            vm.enableContextMenuForPerson = vm.getPersonById(group.attrs.id);
            vm.enableContextMenu = true;
          }

          // Show menu
          const containerRect = stage.container().getBoundingClientRect();
          vm.groupContextMenuTop = containerRect.top + stage.getPointerPosition().y + 4 + 'px';
          vm.groupContextMenuLeft = containerRect.left + stage.getPointerPosition().x + 4 + 'px';
        });
      },
      setupZoom() {
        const vm = this;
        const stage = this.getStage();
        const scaleBy = 1.12;

        stage.on('wheel', (e) => {
          // stop default scrolling
          e.evt.preventDefault();

          if (vm.activeSelectionRectangle) {
            return;
          }

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
      getPersonById(personId) {
        return this.store.persons.filter(person => person.id == personId)[0];
      },
      selectPerson(personId, centerOnStage = true) {
        const stage = this.getStage();
        const personImageNode = stage.findOne('#' + personId);
        stage.fire('click', {target: personImageNode, evt: {}}, true);

        if (centerOnStage) {
          stage.x(personImageNode.x() + stage.width() / 3);
          stage.y(personImageNode.y() + stage.height() / 2);
        }
      },
      setupSelection() {
        const vm = this;
        const stage = this.getStage();
        const layer = this.$refs.layer.getNode();

        const MIN_WIDTH = 100;
        const MAX_WIDTH = 3000;

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

            return newBoundBox;
          },
        });
        layer.add(this.transformer);
        this.resetSelectedNodes();

        var selectionRectangle = new Konva.Rect({
          fill: 'rgba(0, 0, 255, 0.5)',
          visible: false,
        });
        layer.add(selectionRectangle);

        var x1, y1, x2, y2;
        stage.on('mousedown touchstart', (e) => {
          // do nothing if we mousedown on any shape
          if (e.target !== stage) {
            return;
          }
          e.evt.preventDefault();

          vm.activeSelectionRectangle = true;

          const offsetX = localStorage.getItem('stage.x') / this.zoom;
          const offsetY = localStorage.getItem('stage.y') / this.zoom;

          x1 = (offsetX * -1) + stage.getPointerPosition().x;
          y1 = (offsetY * -1) + stage.getPointerPosition().y;

          x2 = (offsetX * -1) + stage.getPointerPosition().x;
          y2 = (offsetY * -1) + stage.getPointerPosition().y;

          selectionRectangle.visible(true);
          selectionRectangle.width(0);
          selectionRectangle.height(0);
        });

        stage.on('mousemove touchmove', (e) => {
          // do nothing if we didn't start selection
          if (!selectionRectangle.visible()) {
            return;
          }
          e.evt.preventDefault();

          const offsetX = localStorage.getItem('stage.x') / this.zoom;
          const offsetY = localStorage.getItem('stage.y') / this.zoom;

          x2 = (offsetX * -1) + stage.getPointerPosition().x;
          y2 = (offsetY * -1) + stage.getPointerPosition().y;

          selectionRectangle.setAttrs({
            x: Math.min(x1, x2) / this.zoom,
            y: Math.min(y1, y2) / this.zoom,
            width: Math.abs(x2 - x1) / this.zoom,
            height: Math.abs(y2 - y1) / this.zoom,
          });
        });

        stage.on('mouseup touchend', (e) => {
          // do nothing if we didn't start selection
          if (!selectionRectangle.visible()) {
            return;
          }
          e.evt.preventDefault();

          vm.activeSelectionRectangle = false;

          // update visibility in timeout, so we can check it in click event
          setTimeout(() => {
            selectionRectangle.visible(false);
          });

          var groups = stage.find('.person-group');
          var selectionRectangleBoundingBox = selectionRectangle.getClientRect();
          const selected = groups.filter((group) =>
            Konva.Util.haveIntersection(
              selectionRectangleBoundingBox,
              group.getClientRect()
            )
          );

          const metaPressed = e.evt.shiftKey || e.evt.ctrlKey || e.evt.metaKey;
          if (metaPressed) {
            vm.selectedNodes = vm.selectedNodes.concat(selected);
          } else {
            vm.selectedNodes = selected;
          }
        });

        // clicks should select/deselect shapes
        stage.on('click tap', function (e) {

          if (vm.activeSelectionRectangle) {
            return;
          }

          // if click on empty area - remove all selections
          if (e.target === stage) {
            vm.resetSelectedNodes();
            return;
          }

          // Allow only specific elements as targets and get their
          // parent group as the actual thing we toggle the selection
          // on.

          // We may have programmatically selected the v-group (but it's
          // not selectable manually).
          let group = e.target.hasName('person-group') ? e.target : null;

          if (e.target.hasName('person-image') || e.target.hasName('person-name')) {
            group = e.target.getParent().getParent();
          }
          if (!group) {
            return;
          }

          // Did we press shift or ctrl?
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

          // if (vm.selectedNodes.length === 1) {
          //   const person = vm.persons.filter(person => person.id == group.id())[0];
          //   vm.onPersonSelected(e, person);
          // } else {
          //   vm.store.setEditedPerson(null);
          // }
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
