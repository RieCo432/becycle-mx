import {defineStore} from "pinia";
import user1Img from "@/assets/images/users/user-1.jpg";
import user2Img from "@/assets/images/users/user-2.jpg";
import user3Img from "@/assets/images/users/user-3.jpg";
import user4Img from "@/assets/images/users/user-4.jpg";
import user5Img from "@/assets/images/users/user-5.jpg";
import user6Img from "@/assets/images/users/user-6.jpg";

export const useChatStore = defineStore('chat',{
    state: ()=>{
        return {
            settingToggle: false,
            openinfo: true,
            activechat: false,
            searchContact: "",
            mobileChatSidebar: false,
            profileinfo: {},
            messFeed: [],
            user: {},
            contacts: [
                {
                    id: 1,
                    fullName: "Kathryn Murphy",
                    role: "Frontend Developer",
                    lastmessage: "Hey! there I'm available",
                    lastmessageTime: "2:30 PM",
                    unredmessage: Math.floor(Math.random() * 10),
                    avatar: user2Img,
                    status: "offline",
                },
                {
                    id: 2,
                    fullName: "Felecia Rower",
                    role: " UI/UX Designer",
                    lastmessage: "Hey! there I'm available",
                    lastmessageTime: "2:30 PM",
                    unredmessage: Math.floor(Math.random() * 10),
                    avatar: user3Img,
                    status: "active",
                },
                {
                    id: 3,
                    fullName: " Aileen Chavez",
                    role: " Backend Developer",
                    lastmessage: "Hey! there I'm available",
                    lastmessageTime: "2:30 PM",
                    unredmessage: Math.floor(Math.random() * 10),
                    avatar: user4Img,
                    status: "offline",
                },
                {
                    id: 4,
                    fullName: "Alec Thompson",
                    role: " Full Stack Developer",
                    lastmessage: "Hey! there I'm available",
                    lastmessageTime: "2:30 PM",
                    unredmessage: Math.floor(Math.random() * 10),
                    avatar: user5Img,
                    status: "active",
                },
                {
                    id: 5,
                    fullName: "Murphy Aileen",
                    role: "Frontend Developer",
                    lastmessage: "Hey! there I'm available",
                    lastmessageTime: "2:30 PM",
                    unredmessage: Math.floor(Math.random() * 10),
                    avatar: user6Img,
                    status: "offline",
                },
            ],
            chats: [
                {
                    id: 1,
                    userId: 1,
                    messages: [
                        {
                            img: user2Img,
                            content: "Hey! How are you?",
                            time: "10:00",
                            sender: "them",
                        },
                        {
                            img: user2Img,
                            content: "Good, I will book the meeting room for you.",
                            time: "10:02",

                            sender: "them",
                        },
                        {
                            content: "Hi, I am good, what about you?",
                            img: user1Img,
                            time: "10:01",
                            sender: "me",
                        },

                        {
                            content: "Thanks, It will be great.",
                            img: user1Img,
                            time: "10:03",
                            sender: "me",
                        },
                        {
                            img: user2Img,
                            content: "Hey! How are you?",
                            time: "10:00",
                            sender: "them",
                        },
                        {
                            img: user2Img,
                            content: "Good, I will book the meeting room for you.",
                            time: "10:02",

                            sender: "them",
                        },
                        {
                            content: "Hi, I am good, what about you?",
                            img: user1Img,
                            time: "10:01",
                            sender: "me",
                        },

                        {
                            content: "Thanks, It will be great.",
                            img: user1Img,
                            time: "10:03",
                            sender: "me",
                        },
                    ],
                },
                {
                    id: 2,
                    userId: 2,
                    messages: [
                        {
                            img: user2Img,
                            content: "Hey! How are you?",
                            time: "10:00",
                            sender: "them",
                        },
                        {
                            img: user2Img,
                            content: "Good, I will book the meeting room for you.",
                            time: "10:02",

                            sender: "them",
                        },
                    ],
                },
                {
                    id: 3,
                    userId: 3,
                    messages: [
                        {
                            img: user2Img,
                            content: "Hey! How are you?",
                            time: "10:00",
                            sender: "them",
                        },
                        {
                            img: user2Img,
                            content: "Good, I will book the meeting room for you.",
                            time: "10:02",

                            sender: "me",
                        },
                    ],
                },
                {
                    id: 4,
                    userId: 4,
                    messages: [
                        {
                            img: user2Img,
                            content: "Hey! How are you?",
                            time: "10:00",
                            sender: "me",
                        },
                        {
                            img: user2Img,
                            content: "Good, I will book the meeting room for you.",
                            time: "10:02",

                            sender: "them",
                        },
                    ],
                },
                {
                    id: 5,
                    userId: 5,
                    messages: [
                        {
                            img: user2Img,
                            content: "Hey! How are you?",
                            time: "10:00",
                            sender: "them",
                        },
                        {
                            img: user2Img,
                            content: "Good, I will book the meeting room for you.",
                            time: "10:02",

                            sender: "them",
                        },
                    ],
                },
            ],
        }
    },
    getters:{
        getprofileinfo: (state) => state.profileinfo,
        // get contacts with search
        getContacts: (state) => {
            if (state.searchContact) {
                return state.contacts.filter((contact) =>
                    contact.fullName
                        .toLowerCase()
                        .includes(state.searchContact.toLowerCase())
                );
            } else {
                return state.contacts;
            }
        },
        getChats: (state) => state.chats,
    },
    actions:{
        toggleUserSetting() {
            this.settingToggle = !this.settingToggle;
        },
        sendMessage(payload) {
            this.messFeed.push(payload);
        },
        //openinfo
        notOpenInfo() {
            this.openinfo = !this.openinfo;
        },
        //open chat
        openChat(data) {
            this.activechat = true;
            this.mobileChatSidebar = false;
            this.user = data;
            this.chats.map((item) => {
                if (item.userId === data.id) {
                    this.messFeed = item.messages;
                }
            });
        },
        openMobileSidebar() {
            this.mobileChatSidebar = !this.mobileChatSidebar;
        },
    }
})