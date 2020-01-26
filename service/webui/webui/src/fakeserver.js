import { Server } from "miragejs"

var server = new Server({
  routes() {
    this.namespace = "/api"

    this.get("/users", () => [
      { id: "1", name: "Luke" },
      { id: "2", name: "Leah" },
      { id: "3", name: "Anakin" },
    ])
  },
})

export default server;
