import { Application } from "stimulus";

// Import controllers
import HelloController from "./controllers/hello_controller";


let application = null

if (module.hot) {
  module.hot.accept() // tell hmr to accept updates

  if (module.hot.data) {
    application = module.hot.data.application // re-use old application if one was passed after update
  }

  module.hot.dispose(data => {
    data.application = application // on disposal of the old version (before reload), pass the old application to the new version
  })
}

if (!application) {
  application = Application.start() // if no application so far, start it
}

application.register("hello", HelloController);
