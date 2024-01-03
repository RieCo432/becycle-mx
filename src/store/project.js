import {defineStore} from "pinia";
import { v4 as uuidv4 } from "uuid";
import { useToast } from "vue-toastification";
import av1Img from "@/assets/images/avatar/av-1.svg";
import av2Img from "@/assets/images/avatar/av-2.svg";
const toast = useToast();
export const useProjectStore = defineStore('project', {
    state: ()=>{
        return {
            addmodal: false,
            isLoading: null,
            // for edit
            editModal: false,
            editName: "",
            editassignto: null,
            editStartDate: null,
            editEndDate: null,
            editcta: null,
            editId: null,
            editdesc: null,

            projects: [
                {
                    id: uuidv4(),
                    assignto: [
                        {
                            image: av1Img,
                            title: "Mahedi Amin",
                        },
                        {
                            image: av2Img,
                            title: "Sovo Haldar",
                        },
                        {
                            image: av2Img,
                            title: "Rakibul Islam",
                        },
                    ],
                    name: "Management Dashboard ",
                    des: "Amet minim mollit non deserunt ullamco est sit aliqua dolor do amet sint.",
                    startDate: "2022-10-03",
                    endDate: "2022-10-06",
                    progress: 75,
                    category: [
                        {
                            value: "team",
                            label: "team",
                        },
                        {
                            value: "low",
                            label: "low",
                        },
                    ],
                },
                {
                    id: uuidv4(),
                    assignto: [
                        {
                            image: av1Img,
                            title: "Mahedi Amin",
                        },
                        {
                            image: av2Img,
                            title: "Sovo Haldar",
                        },
                        {
                            image: av2Img,
                            title: "Rakibul Islam",
                        },
                    ],
                    name: "Business Dashboard ",
                    des: "Amet minim mollit non deserunt ullamco est sit aliqua dolor do amet sint.",
                    startDate: "2022-10-03",
                    endDate: "2022-10-10",
                    progress: 50,

                    category: [
                        {
                            value: "team",
                            label: "team",
                        },
                        {
                            value: "low",
                            label: "low",
                        },
                    ],
                },
            ],
        }
    },
    actions:{
        //
        addProject(data) {
            this.isLoading = true;

            setTimeout(() => {
                this.projects.unshift(data);
                this.isLoading = false;
                toast.success("Project added", {
                    timeout: 2000,
                });
            }, 1500);
            this.addmodal = false;
        },
        // removeProject
        removeProject(data) {
            this.projects = this.projects.filter((item) => item.id !== data.id);
            toast.error("Project Removed", {
                timeout: 2000,
            });
        },
        // updateProject
        updateProject(data) {
            this.projects.findIndex((item) => {
                if (item.id === data.id) {
                    // store data
                    this.editId = data.id;
                    this.editName = data.name;
                    this.editassignto = data.assignto;
                    this.editStartDate = data.startDate;
                    this.editEndDate = data.endDate;
                    this.editcta = data.category;
                    this.editdesc = data.des;
                    this.editModal = !this.editModal;
                    // set data to data
                    item.name = data.name;
                    item.des = data.des;
                    item.startDate = data.startDate;
                    item.endDate = data.endDate;
                    item.assignto = data.assignto;
                    item.progress = data.progress;
                    item.category = data.category;
                }
            });
        },
        // openProject
        openProject() {
            this.addmodal = true;
        },
        // closeModal
        closeModal() {
            this.addmodal = false;
        },
        // closeEditModal
        closeEditModal() {
            this.editModal = false;
        },
    }
})