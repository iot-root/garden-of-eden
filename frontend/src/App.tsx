import type { Component } from 'solid-js';

import { MobileNavbar } from '@/components/nav/mobile-navbar';
import styles from './App.module.css';
import { Modal } from './components/ui/modal';

const App: Component = (props) => {
  return (
    <div class={styles.App}>
      {props.children}
      <Modal />
      <MobileNavbar />
    </div>
  );
};

export default App;
