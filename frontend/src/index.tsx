/* @refresh reload */
import { Route, Router } from "@solidjs/router";
import { lazy } from "solid-js";
import { render } from 'solid-js/web';
import App from "./App";
import './index.css';


const root = document.getElementById('root');

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    'Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?',
  );
}

const Home = lazy(() => import("./pages/home"));
const Logs = lazy(() => import("./pages/logs"));
const Notifications = lazy(() => import("./pages/notifications"));

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/logs" component={Logs} />
      <Route path="/notifications" component={Notifications} />
    </Router>
  ),
  root!);
