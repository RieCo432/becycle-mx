const routes = [
  {
    path: "/",
    name: "Layout",
    redirect: "/home",
    component: () => import("@/Layout/index.vue"),
    children: [
      {
        path: "/home",
        name: "home",
        component: () => import("@/views/index.vue"),
      },
    ],
  },
];

export default routes;
