import {defineStore} from "pinia";
import { v4 as uuidv4 } from "uuid";
import { useToast } from "vue-toastification";
import av1Img from "@/assets/images/avatar/av-1.svg";
import av2Img from "@/assets/images/avatar/av-2.svg";
const toast = useToast();

export const useTodoStore = defineStore('todo',{
    state:()=>({
        addModal: false,
        editModal: false,
        todoSearch: "",
        eidtModalId: null,
        mobileTodoSidebar: false,
        isLoading: null,
        isSkeleton: true,
        trashTodo: [],

        // editobject
        editItem: {},
        todos: [
            {
                id: uuidv4(),
                image: [
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
                title:
                    "laboriosam mollitia et enim quasi adipisci quia provident illum",
                isDone: false,
                isfav: false,
                catagory: [
                    {
                        value: "team",
                        label: "team",
                    },
                ],
            },
            {
                id: uuidv4(),
                image: [
                    {
                        image: av2Img,
                        title: "Rakibul Islam",
                    },
                ],
                title:
                    "Amet minim mollit non deserunt ullamco est sit aliqua dolor do amet sint.",
                isDone: true,
                isfav: true,
                catagory: [
                    {
                        value: "low",
                        label: "low",
                    },
                ],
            },
            {
                id: uuidv4(),
                image: [
                    {
                        image: av2Img,
                        title: "Sovo Haldar",
                    },
                    {
                        image: av2Img,
                        title: "Rakibul Islam",
                    },
                ],
                title:
                    "Amet minim mollit non deserunt ullamco est sit aliqua dolor do amet sint.",
                isDone: true,
                isfav: true,
                catagory: [
                    {
                        value: "medium",
                        label: "medium",
                    },
                    {
                        value: "low",
                        label: "low",
                    },
                ],
            },
            {
                id: uuidv4(),
                image: [
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
                title: "illo expedita consequatur quia in",
                isDone: false,
                isfav: false,
                catagory: [
                    {
                        value: "high",
                        label: "high",
                    },
                    {
                        value: "low",
                        label: "low",
                    },
                ],
            },
            {
                id: uuidv4(),
                image: [
                    {
                        image: av2Img,
                        title: "Rakibul Islam",
                    },
                ],
                title: "illo expedita consequatur quia in",
                isDone: false,
                isfav: false,
                catagory: [
                    {
                        value: "update",
                        label: "update",
                    },
                ],
            },
        ],
    }),
    getters:{
        todosGetter: (state) =>
            state.todoSearch === ""
                ? state.todos
                : state.todos.filter((item) => {
                    return item.title
                        .toLowerCase()
                        .replace(/\s+/g, "")
                        .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                }),

        // trashTodo
        trashTodoGetter: (state) =>
            state.todoSearch   === ""
                ? state.trashTodo
                : state.trashTodo.filter((item) => {
                    return item.title
                        .toLowerCase()
                        .replace(/\s+/g, "")
                        .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                }),
        // isDone with search
        isDone: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.isDone === true)
                : state.todos
                    .filter((item) => item.isDone === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
        //isFav with search
        isFav: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.isfav === true)
                : state.todos
                    .filter((item) => item.isfav === true)
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
        //high with search
        high: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.catagory[0].value === "high")
                : state.todos
                    .filter((item) => item.catagory[0].value === "high")
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
        //medium with search
        medium: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.catagory[0].value === "medium")
                : state.todos
                    .filter((item) => item.catagory[0].value === "medium")
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
        //low with search
        low: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.catagory[0].value === "low")
                : state.todos
                    .filter((item) => item.catagory[0].value === "low")
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
        //team with search
        team: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.catagory[0].value === "team")
                : state.todos
                    .filter((item) => item.catagory[0].value === "team")
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
        //update with search
        update: (state) =>
            state.todoSearch === ""
                ? state.todos.filter((item) => item.catagory[0].value === "update")
                : state.todos
                    .filter((item) => item.catagory[0].value === "update")
                    .filter((item) => {
                        return item.title
                            .toLowerCase()
                            .replace(/\s+/g, "")
                            .includes(state.todoSearch.toLowerCase().replace(/\s+/g, ""));
                    }),
    },
    actions:{
        // open todo
        openTodo() {
            this.addModal = true;
        },
        closeTodo() {
            this.addModal = false;
        },
        OPEN_EDIT_MODAL(itemId) {
            this.editModal = true;
            this.eidtModalId = itemId;
            //console.log(itemId); // find data id
        },
        closeEditModal() {
            this.editModal = false;
        },
        GET_TODO(todo) {
            this.todo = todo;
        },
        addTodo(data) {
            // add data into array by unshift

            // add data after 2 sec delay and set loading to false
            this.isLoading = true;
            this.mobileTodoSidebar = false;
            setTimeout(() => {
                this.todos.unshift(data);
                this.isLoading = false;
                toast.success("Task added", {
                    timeout: 2000,
                });
            }, 1500);

            this.addModal = false;
        },
        editTodo(todo) {
            // if state editModal false make true
            this.todos.findIndex((item) => {
                if (item.id === todo.id) {
                    this.editItem = item;
                    this.editModal = !this.editModal;
                    // find index
                    let index = this.todos.indexOf(item);

                    this.todos.splice(index, 1, {
                        // give a id into eidtModalId

                        id: todo.id,
                        title: todo.title,
                        isDone: todo.isDone,
                        isfav: todo.isfav,
                        image: todo.image,
                        catagory: todo.catagory,
                    });
                }
            });
            // console.log(todo, "to theke patahano");
        },
        removeTodo(todo) {
            var todos = this.todos;
            todos.splice(todos.indexOf(todo), 1);
            this.trashTodo.unshift(todo);
            toast.error("Task Delete", {
                timeout: 2000,
            });
        },
        COMPLETE_TODO(todo) {
            todo.completed = !todo.completed;
        },
        CLEAR_TODO() {
            this.todo = "";
        },
        // sorting
        sortAZ() {
            this.todos.sort((a, b) => {
                return a.title.localeCompare(b.title);
            });
        },
        sortZA() {
            this.todos.sort((a, b) => {
                return b.title.localeCompare(a.title);
            });
        },
        // RESET_SORT
        resetSort() {
            this.todos.sort((a, b) => {
                return a.id.localeCompare(b.id);
            });
        },
        openMobileTodoSidebar() {
            this.mobileTodoSidebar = true;
        },
        closeMobileTodoSidebar() {
            this.mobileTodoSidebar = false;
        },
    }
})