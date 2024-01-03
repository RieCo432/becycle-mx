import {defineStore} from "pinia";
import { v4 as uuidv4 } from "uuid";
import { useToast } from "vue-toastification";
import av1Img from "@/assets/images/avatar/av-1.svg";
import av2Img from "@/assets/images/avatar/av-2.svg";
import av3Img from "@/assets/images/avatar/av-3.svg";
const toast = useToast();

export const useEmailStore = defineStore('email', {
    state: () => {
        return {
            image: av1Img,
            addModal: false,
            search: "",
            singleEmailModal: false,
            mobileEmailSidebar: false,
            storeEmail: {},
            isCheckAll: false,
            emailLoading: false,
            trashEmails: [],
            emails: [
                {
                    id: uuidv4(),
                    image: av1Img,
                    title: "Pay bills & win up to 600$ Cashback! ",
                    desc: " - Congratulations on your iRun Coach subscription. You made no space for excuses and you decided on a healthier and happier life...",
                    isfav: false,
                    sent: false,
                    draft: true,
                    spam: false,
                    trash: false,
                    personal: false,
                    social: true,
                    promotions: true,
                    lastime: "12:20 pm",
                    busines: true,
                    checked: false,
                    isread: false,
                    isspam: true,
                    isdelate: false,
                },
                {
                    id: uuidv4(),
                    image: av2Img,
                    title: "Pay bills & win up to 600$ Cashback! ",
                    desc: " - Congratulations on your iRun Coach subscription. You made no space for excuses and you decided on a healthier and happier life...",
                    isfav: true,
                    sent: false,
                    draft: false,
                    spam: false,
                    trash: false,
                    personal: false,
                    social: false,
                    promotions: false,
                    lastime: "12:20 pm",
                    checked: false,
                    busines: false,
                    isread: false,
                    isspam: true,
                    isdelate: false,
                },
                {
                    id: uuidv4(),
                    image: av3Img,
                    title: "1-Pay bills & win up to 600$ Cashback! ",
                    desc: " - Congratulations on your iRun Coach subscription. You made no space for excuses and you decided on a healthier and happier life...",
                    isfav: true,
                    sent: false,
                    draft: true,
                    spam: false,
                    trash: false,
                    personal: true,
                    social: false,
                    promotions: false,
                    lastime: "12:20 pm",
                    checked: false,
                    busines: false,
                    isread: false,
                    isspam: false,
                    isdelate: false,
                },
                {
                    id: uuidv4(),
                    image: av2Img,
                    title: "1-Pay bills & win up to 600$ Cashback! ",
                    desc: " - Congratulations on your iRun Coach subscription. You made no space for excuses and you decided on a healthier and happier life...",
                    isfav: true,
                    sent: true,
                    draft: false,
                    spam: false,
                    trash: false,
                    personal: true,
                    social: false,
                    promotions: false,
                    lastime: "12:20 pm",
                    checked: false,
                    busines: false,
                    isread: false,
                    isspam: false,
                    isdelate: false,
                },
            ],
        }
    },
    getters: {
        // emails with search
        emailsGet: (state) =>
            state.search === ""
                ? state.emails
                : state.emails.filter((item) => {
                    return item.title
                        .toLowerCase()
                        .replace(/\s+/g, "")
                        .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                }),
        // fav email with search
        favEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.isfav === true)
                : state.emails
                    .filter((item) => item.isfav === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // sent email with search
        sentEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.sent === true)
                : state.emails
                    .filter((item) => item.sent === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // draft email with search
        draftEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.draft === true)
                : state.emails
                    .filter((item) => item.draft === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // personal email with search
        personalEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.personal === true)
                : state.emails
                    .filter((item) => item.personal === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // social email with search
        socialEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.social === true)
                : state.emails
                    .filter((item) => item.social === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // promotions email with search
        promotionsEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.promotions === true)
                : state.emails
                    .filter((item) => item.promotions === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // busines email with search
        businesEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.busines === true)
                : state.emails
                    .filter((item) => item.busines === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        // span email with search
        spamEmails: (state) =>
            state.search === ""
                ? state.emails.filter((item) => item.isspam === true)
                : state.emails
                    .filter((item) => item.isspam === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                    }),
        trashEmailsGet: (state) =>
            state.search === ""
                ? state.trashEmails
                : state.trashEmails.filter((item) => {
                    return item.title
                        .toLowerCase()
                        .replace(/\s+/g, "")
                        .includes(state.search.toLowerCase().replace(/\s+/g, ""));
                }),
    },
    actions: {
        //openEmail
        openEmail() {
            this.addModal = true;
        },
        // sendEmail
        sendEmail(payload) {
            this.emails.unshift(payload);
            this.emailLoading = true;
            setTimeout(() => {
                this.emailLoading = false;
                toast.success("Email Send", {
                    timeout: 2000,
                });
            }, 1500);
        },
        // deleteEmail
        deleteEmail(payload) {
            var emails = this.emails;
            emails.splice(emails.indexOf(payload), 1);
            // store email delatedEmails
            this.trashEmails.unshift(payload);
            toast.error("Email Delate", {
                timeout: 2000,
            });
        },
        // checkAll
        checkAll() {
            this.isCheckAll = !this.isCheckAll;
            this.emails.forEach((item) => {
                item.checked = this.isCheckAll;
            });
        },
        openSingle(payload) {
            this.storeEmail = payload;
            this.singleEmailModal = !this.singleEmailModal;
            payload.isread = true;
        },
        openMobileEmailSidebar() {
            this.mobileEmailSidebar = !this.mobileEmailSidebar;
        },
        closeMobileEmailSidebar() {
            this.mobileEmailSidebar = false;
        },
        closeDetailsEmail() {
            this.singleEmailModal = false;
        },
    }
})