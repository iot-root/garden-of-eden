import type { Component } from 'solid-js';

// UI
import { Button } from "../components/Button/Button";
import { Switches } from '../components/Switches/Switches';

// Senors
import { GetDistance } from "../endpoints/distance";
import { GetHumidity } from "../endpoints/humidity";
import { GetBrightness, SetBrightness, TurnOffLight, TurnOnLight } from "../endpoints/light";
import { GetPCBTemp } from "../endpoints/pcb-temp";
import { GetPumpSpeed, GetPumpStats, SetPumpSpeed, TurnOffPump, TurnOnPump } from "../endpoints/pump";
import { GetTemp, } from "../endpoints/temperature";

import styles from './App.module.css';

const App: Component = () => {
  return (
    <div class={styles.App}>
      <Switches title="Lights">
        <Button text='On' cb={TurnOnLight} />
        <Button text='Off' cb={TurnOffLight} />
        <Button text='Set Brightness' cb={SetBrightness} />
        <Button text='Check Brightness' cb={GetBrightness} />
      </Switches>
      
      <Switches title="Pump">
        <Button text='On' cb={TurnOnPump} />
        <Button text='Off' cb={TurnOffPump} />
        <Button text='Set Speed' cb={SetPumpSpeed} />
        <Button text='Check Speed' cb={GetPumpSpeed} />
      </Switches>
  
      <Switches title="Data">
        <Button text='Air Temp' cb={GetTemp} />
        <Button text='Humidity' cb={GetHumidity} />
        <Button text='Water Level' cb={GetDistance} />
        <Button text='Pump Stats' cb={GetPumpStats} />
        <Button text='PCB Temp' cb={GetPCBTemp} />
      </Switches>
    </div>
  );
};

export default App;
