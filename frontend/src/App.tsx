import type { Component } from 'solid-js';

import { MobileNavbar } from '@/components/nav/mobile-navbar';
import styles from './App.module.css';

const App: Component = (props) => {
  return (
    <div class={styles.App}>
      {props.children}
      <MobileNavbar />
    </div>
  );
};

export default App;
