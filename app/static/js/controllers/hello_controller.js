import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["output"];

  greet() {
    this.outputTarget.textContent = "Hello, Stimulus!!!";
    console.log("Hello, Stimulus!!!");
  }
}
