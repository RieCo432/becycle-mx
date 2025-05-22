<template>
  <div class="h-[750px] w-full">
    <l-map
        :center="center"
        v-model:center="center"
        v-model:zoom="zoom"
        v-model:bounds="bounds"
        :zoom="zoom"
        :minZoom="14"
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
        <l-popup :options="{
          minWidth: 400,
        }">
            <div class="grid grid-cols-2">
              <div class="col-span-2">
                <table class="border-collapse border border-slate-600">
                  <caption>Reports for this segment</caption>
                  <thead>
                  <tr>
                    <th class="border border-slate-600" scope="col">Title</th>
                    <th class="border border-slate-600" scope="col">Description</th>
                  </tr>
                  </thead>
                  <tbody>
                  <tr v-for="report in markerReports" :key="report.id">
                    <td class="border border-slate-600" >{{report.title}}</td>
                    <td class="border border-slate-600" >{{report.description}}</td>
                  </tr>
                  </tbody>
                </table>
              </div>
              <div class="col-span-2">
                <div class="grid grid-cols-6 gap-3">
                  <div class="col-span-4">
                    <Select
                        :options="roadSegmentReportTypes"
                        class-label="dark:text-slate-800"
                        label="Add Report"
                        v-model="newReportType"
                        name="newReportType"
                        class-input="w-full"/>
                  </div>
                  <div class="col-span-2 content-end">
                    <Button class="btn-light btn-block mt-auto align-bottom" @click="submitNewReport">Submit</Button>
                  </div>
                </div>
              </div>
            </div>
        </l-popup>
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
import {LMap, LTileLayer, LGeoJson, LMarker, LPopup} from '@vue-leaflet/vue-leaflet';
import Select from '@/components/Select';
import Button from '@/components/Button';
// eslint-disable-next-line no-unused-vars
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import requests from '@/requests';

export default {
  name: 'Map',
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
    LMarker,
    LPopup,
    Select,
    Button,
  },
  data() {
    return {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      geojson: null,
      center: [57.148, -2.094],
      zoom: 18,
      markerLatLng: null,
      markerReports: [],
      loadingGeoJson: true,
      bounds: null,
      attribution: 'OpenStreetMap, Ordnance Survey Maps',
      optionsStyle: (feature) => {
        const score = feature.properties.reports.map((report) => (report.scoreModifier)).reduce((a, b) => a+b, 0);
        if (score !== 0) {
          const indexInFeatures = this.geojson.features.findIndex((f) => f.properties.id === feature.properties.id);
        }
        const r = Math.round(255 * Math.max(Math.min(-score + 5, 5), 0) / 5);
        const g = Math.round(255 * Math.max(Math.min(score + 5, 5), 0) / 5);
        return {
          color: `#${r.toString(16)}${g.toString(16)}00`,
          weight: 5,
        };
      },
      roadSegmentReportTypes: [],
      newReportType: null,
      newReportRoadSegmentId: null,
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
      this.markerLatLng = [
        (evt.layer.feature.geometry.coordinates[0][1] + evt.layer.feature.geometry.coordinates[1][1]) / 2,
        (evt.layer.feature.geometry.coordinates[0][0] + evt.layer.feature.geometry.coordinates[1][0]) / 2,
      ];
      this.markerReports = evt.layer.feature.properties.reports;
      this.newReportRoadSegmentId = evt.layer.feature.properties.id;
    },
    submitNewReport() {
      this.loadingGeoJson = true;
      requests.postNewRoadSegmentReport(this.newReportRoadSegmentId, this.newReportType).then((response) => {
        const roadSegmentGeoJson = JSON.parse(response.data);
        const indexOfRoadSegment = this.geojson.features.findIndex((feature) => feature.properties.id === this.newReportRoadSegmentId);
        this.geojson.features.splice(indexOfRoadSegment, 1, roadSegmentGeoJson);
        this.loadingGeoJson = false;
        this.markerReports = roadSegmentGeoJson.properties.reports;
        this.newReportType = null;
      });
    },
  },
  created() {
    requests.getRoadSegmentReportTypes().then((response) => {
      this.roadSegmentReportTypes = response.data.map((type) => (
        {
          label: `${type.title}: ${type.description}`,
          value: type.id,
        }
      ));
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
