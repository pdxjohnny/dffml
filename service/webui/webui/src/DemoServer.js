import { Server } from "miragejs"

export default class DemoServer {
  constructor() {
    this.server = null;
  }

  start() {
    if (this.server !== null) {
      this.stop();
    }

    this.server = new Server({
      routes() {
        this.namespace = "/api"

        this.get("/service/files", () => [
          {
            filename: 'file.csv',
            size: 3271,
          },
          {
            filename: 'there.csv',
            size: 2310,
          },
          {
            filename: 'down1/other.csv',
            size: 7157,
          },
          {
            filename: 'down1/down2/another.csv',
            size: 56190,
          },
          {
            filename: 'down1/down2/also.csv',
            size: 4654,
          },
          {
            filename: 'down1/down3/here.csv',
            size: 12716,
          },
        ])
      },
    });
  }

  stop() {
    this.server.shutdown();
  }
}
