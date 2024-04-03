<template>
  <div class="h-[750px] w-full">
    <l-map
        :center="center"
        v-model:center="center"
        v-model:zoom="zoom"
        v-model:bounds="bounds"
        :zoom="zoom"
        :minZoom="3"
        :maxZoom="18"
        :zoomAnimation="true"
        @update:bounds="boundsUpdated"
        ref="mapView"
        @ready="boundsUpdated(this.$refs.mapView.leafletObject.getBounds())">
      <l-tile-layer
          :url="url"
          attribution="attribution"
      ></l-tile-layer>

      <l-marker v-if="markerLatLng" :lat-lng="markerLatLng">
        <l-popup>Test</l-popup>
      </l-marker>
      <l-geo-json
          v-if="!loadingGeoJson"
          :geojson="geojson"
          @click="geojsonClick"
          :options-style="optionsStyle"
      ></l-geo-json>


    </l-map>
  </div>
</template>

<script>
// DON'T load Leaflet components here!
// Its CSS is needed though, if not imported elsewhere in your application.
import {LMap, LTileLayer, LGeoJson, LTooltip, LMarker, LPopup, LLayerGroup} from '@vue-leaflet/vue-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import requests from '@/requests';

export default {
  name: 'Map',
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
    LTooltip,
    LMarker,
    LPopup,
    LLayerGroup,
  },
  data() {
    return {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      geojson: null,
      center: [57.147, -2.095],
      zoom: 17,
      markerLatLng: null,
      loadingGeoJson: true,
      bounds: null,
      attribution: 'OpenStreetMap, Ordnance Survey Maps',
      optionsStyle: (feature) => {
        const score = feature.properties.reports.map((report) => (report.scoreModifier)).reduce((a, b) => a+b, 0);
        const r = Math.round(255 * Math.max(Math.min(-score + 5, 5), 0) / 5);
        const g = Math.round(255 * Math.max(Math.min(score + 5, 5), 0) / 5);
        return {
          color: `#${r.toString(16)}${g.toString(16)}00`,
          weight: 5,
        };
      },
    };
  },
  methods: {
    boundsUpdated(bounds) {
      const northBound = bounds._northEast.lat;
      const eastBound = bounds._northEast.lng;
      const southBound = bounds._southWest.lat;
      const westBound = bounds._southWest.lng;
      this.loadingGeoJson = true;
      requests.getBboxGeojson(northBound, eastBound, southBound, westBound).then((response) => {
        this.geojson = JSON.parse(response.data);
        this.loadingGeoJson = false;
      });
    },
    geojsonClick(evt) {
      console.log(evt);
      this.markerLatLng = [
        (evt.layer.feature.geometry.coordinates[0][1] + evt.layer.feature.geometry.coordinates[1][1]) / 2,
        (evt.layer.feature.geometry.coordinates[0][0] + evt.layer.feature.geometry.coordinates[1][0]) / 2,
      ];
    },
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
