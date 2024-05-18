import type { Component } from 'solid-js';
import { createSignal } from 'solid-js';

import { AppBox } from '@/components/containers/app-box';
import { Camera } from '@/components/content/camera';
import { Log } from '@/components/content/log';
import { Schedule } from '@/components/content/schedule';
import Sensors from '@/components/content/sensors';
import { MobileNavbar } from '@/components/nav/mobile-navbar';
import { Notifications } from '@/content/notifications';
import styles from './App.module.css';
import { CreateSchedule } from './components/forms/create-schedule';

const App: Component = (props) => {
  const [getSensor, setSensor] = createSignal("")
  const [getMin, setMin] = createSignal(0)
  const [getHour, setHour] = createSignal(0)
  const [getDay, setDay] = createSignal(0)
  const [getState, setState] = createSignal("on")
  const [getBrightness, setBrightness] = createSignal(100)
  const [getSpeed, setSpeed] = createSignal(100)

  return (
    <div class={styles.App}>
      <AppBox>
        <Sensors />
        <Schedule />
        <Notifications />
        <Log />
        <Camera />
        <CreateSchedule />
        <MobileNavbar />
      </AppBox>
    </div>
  );
};

export default App;
