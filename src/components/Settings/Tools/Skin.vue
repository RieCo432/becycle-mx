<template>
  <div>
    <div class="col-span-12 text-slate-600 dark:text-slate-300 text-base mb-2">
      Skin
    </div>
    <div class="grid md:grid-cols-3 grid-cols-1 gap-3">
      <div v-for="(item, i) in skins" :key="i">
        <label
          :for="`skin_id${i}`"
          class="flex items-center text-sm text-slate-500 dark:text-slate-400 cursor-pointer"
        >
          <input
            class="hidden"
            type="radio"
            name="sidebar"
            :id="`skin_id${i}`"
            :value="item.value"
            v-model="skin"
          />

          <span
            :class="item.value === skin ? 'shadow-inset-4' : ''"
            class="flex-none h-4 w-4 bg-white dark:bg-transparent rounded-full border border-secondary-500 inline-block ltr:mr-3 rtl:ml-3 transition-all duration-150"
          ></span>
          {{ item.label }}
        </label>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      skin: this.$store.themeSettingsStore.skin,
      skins: [
        {
          value: "default",
          label: "Default",
        },
        {
          value: "bordered",
          label: "Bordered",
        },
      ],
    };
  },

  mounted() {
  },

  watch: {
    skin: {
      handler() {
        switch (this.skin) {
          case "default":
            this.$store.themeSettingsStore.skin = this.skin;

            document.body.classList.remove("skin--bordered");
            document.body.classList.add("skin--default");
            localStorage.setItem("skin", this.skin);
            break;
          case "bordered":
            this.$store.themeSettingsStore.skin = this.skin;
            // set body class by skin name
            document.body.classList.remove("skin--default");
            document.body.classList.add("skin--bordered");

            localStorage.setItem("skin", this.skin);

            break;
          default:
            this.$store.themeSettingsStore.skin = this.skin;

            // set body class by skin name
            document.body.classList.remove("skin--bordered");
            document.body.classList.add("skin--default");
            localStorage.setItem("skin", this.skin);
        }
      },
      immediate: true,
    },
  },
};
</script>
<style lang="css">
.shadow-inset-4 {
  box-shadow: inset 0 0 0 4px #111112;
}
.dark .shadow-inset-4 {
  box-shadow: inset 0 0 0 4px #ccc;
}
</style>
