<template>
  <div class="h-[750px] w-full">
    <l-map
        :center="center"
        v-model="zoom"
        v-model:zoom="zoom"
        :zoom="zoom"
        :minZoom="3"
        :maxZoom="18"
        :zoomAnimation="true"
    >
      <l-tile-layer :url="url" :attribution=attribution></l-tile-layer>
      <l-geo-json v-if="!loadingGeoJson" :geojson="geojson"></l-geo-json>
    </l-map>
  </div>
</template>

<script>
// DON'T load Leaflet components here!
// Its CSS is needed though, if not imported elsewhere in your application.
import 'leaflet/dist/leaflet.css';
import {LMap, LTileLayer, LGeoJson} from '@vue-leaflet/vue-leaflet';
import requests from '@/requests';

export default {
  name: 'Map',
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
  },
  data() {
    return {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      geojson: null,
      center: [57.15, -2.09],
      zoom: 15,
      loadingGeoJson: true,
      attribution:
          '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    };
  },
  created() {
    requests.getGeoJson().then((response) => {
      this.geojson = JSON.parse(response.data);
      this.loadingGeoJson = false;
    });
  },
};
</script>

<style lang="scss">
.leaflet-control {
  z-index: 0 !important;
}
.leaflet-control-container {
  z-index: 555 !important;
  position: relative;
}
</style>
