import { defineStore } from 'pinia';

export const useThemeSettingsStore = defineStore('themeSettings',{
    state: () => ({
        sidebarCollaspe: false,
        sidebarHidden: false,
        mobielSidebar: false,
        semidark: false,
        semiDarkTheme: "semi-light",
        monochrome: false,
        isDark: false,
        skin: "default",
        theme: "light",
        isOpenSettings: false,
        cWidth: "full",
        menuLayout: "vertical",
        navbarType: "sticky",
        isMouseHovered: false,
        footerType: "static",
        direction: false,
        chartColors: {
            title: "red",
        },
    }),
    actions: {
        setSidebarCollasp() {
            this.sidebarCollasp = !this.sidebarCollasp;
        },

        toogleDark() {
            this.isDark = !this.isDark;
            document.body.classList.remove(this.theme);
            this.theme = this.theme === "dark" ? "light" : "dark";
            document.body.classList.add(this.theme);
            localStorage.setItem("theme", this.theme);
        },

        toggleMonochrome() {
            const isMonochrome = (localStorage.getItem('monochrome') !== null);
            if(isMonochrome) {
                localStorage.removeItem("monochrome");
                document.getElementsByTagName( 'html' )[0].classList.remove('grayscale');
                return;
            } 
            localStorage.setItem("monochrome", true);
            document.getElementsByTagName( 'html' )[0].classList.add('grayscale');
            return;
        },

        toggleSettings() {
            this.isOpenSettings = !this.isOpenSettings;
        },
        toggleMsidebar() {
            this.mobielSidebar = !this.mobielSidebar;
        },
        toggleSemiDark() {
            this.semidark = !this.semidark;
            this.semiDarkTheme = this.semidark ? "semi-dark" : "semi-light";
            document.body.classList.toggle(this.semiDarkTheme);
            localStorage.setItem("semiDark", this.semidark);
        },
    },
})