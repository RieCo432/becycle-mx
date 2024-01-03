import {defineStore} from "pinia";
import { v4 as uuidv4 } from "uuid";
import { useToast } from "vue-toastification";
import av1Img from "@/assets/images/avatar/av-1.svg";
import av2Img from "@/assets/images/avatar/av-2.svg";

const toast = useToast();

export const useKanbanStore = defineStore('kanban',{
    state: () => {
        return {
            columModal: false,
            taskModal: false,
            isLoading: null,
            openTaskId: null,
            // for edit
            editModal: false,
            editName: "",
            editassignto: null,
            editStartDate: null,
            editEndDate: null,
            editcta: null,
            editId: null,
            editdesc: null,
            columns: [
                {
                    id: uuidv4(),
                    name: "To Do",
                    color: "#4669FA",
                    tasks: [
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
                            name: "CRM Dashboard ",
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
                            name: "Dashcode Example Kanban",
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
                    ],
                },
                {
                    id: uuidv4(),
                    name: "In Progress",
                    color: "#FA916B",
                    tasks: [
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
                    ],
                },
                {
                    id: uuidv4(),
                    name: "Done",
                    color: "#50C793",
                    tasks: [
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
                    ],
                },
            ],
        }
    },
    actions: {
        // add column
        addColumn(data) {
            this.isLoading = true;
            setTimeout(() => {
                this.columns.unshift(data);
                this.isLoading = false;
                toast.success("Column added", {
                    timeout: 2000,
                });
            }, 1500);
            this.columModal = false;
        },
        // delete column
        delateColumn(data) {
            this.columns = this.columns.filter((item) => item.id !== data);

            toast.error("Column deleted", {
                timeout: 2000,
            });
        },
        // openColumn
        openColumn() {
            this.columModal = true;
        },
        // open task
        openTask(data) {
            this.columns.find((item) => {
                if (item.id === data.id) {
                    this.taskModal = true;
                    this.openTaskId = data.id;
                }
            });
        },
        // addTask by id
        addTask(data) {
            // sstore data in openid task
            this.columns.find((item) => {
                if (item.id === this.openTaskId) {
                    item.tasks.unshift(data);
                    this.taskModal = false;
                }
            });
        },
        removeTask(data) {
            this.columns.find((item) => {
                // item.tasks = item.tasks.filter((inc) => inc.id !== data.id);
                item.tasks.map((innerItem) => {
                    if (innerItem.id === data.id) {
                        // find index
                        const index = item.tasks.indexOf(innerItem);
                        // remove item
                        item.tasks.splice(index, 1);
                        // toas notification
                        toast.error("Task deleted", {
                            timeout: 2000,
                        });
                    }
                });
            });
        },
        // update task
        updateTask(data) {
            this.columns.find((item) => {
                item.tasks.findIndex((innerItem) => {
                    if (innerItem.id === data.id) {
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
                        innerItem.name = data.name;
                        innerItem.des = data.des;
                        innerItem.startDate = data.startDate;
                        innerItem.endDate = data.endDate;
                        innerItem.assignto = data.assignto;
                        innerItem.progress = data.progress;
                        innerItem.category = data.category;
                    }
                });
            });
        },
    }
})