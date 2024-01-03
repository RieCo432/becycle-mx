<template>
  <video-player
    class="video-player vjs-big-play-centered mx-auto"
    src="https://vjs.zencdn.net/v/oceans.mp4"
    poster="https://vjs.zencdn.net/v/oceans.png"
    playsinline
    controls
    :loop="true"
    :volume="0.6"
    :height="320"
    :playback-rates="[0.7, 1.0, 1.5, 2.0]"
    responsive
    fluid
  />
</template>

<script>
import { defineComponent } from "vue";
import { VideoPlayer } from "@videojs-player/vue";
import "video.js/dist/video-js.css";

export default defineComponent({
  components: {
    VideoPlayer,
  },
});
</script>
