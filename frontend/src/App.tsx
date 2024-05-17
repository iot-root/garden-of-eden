import type { Component } from 'solid-js';
import { createSignal } from 'solid-js';

// ui
import { Button } from "../components/Button/Button";
import { Switches } from '../components/Switches/Switches';

// senors
import { GetDistance } from "../endpoints/distance";
import { GetHumidity } from "../endpoints/humidity";
import { GetBrightness, SetBrightness, TurnOffLight, TurnOnLight } from "../endpoints/light";
import { GetPCBTemp } from "../endpoints/pcb-temp";
import { GetPumpSpeed, GetPumpStats, SetPumpSpeed, TurnOffPump, TurnOnPump } from "../endpoints/pump";
import { GetTemp, } from "../endpoints/temperature";

// schedule
import { addSchedule, deleteAllSchedules, getAllSchedules } from '../endpoints/schedule';

// styles
import styles from './App.module.css';

const App: Component = () => {
  const [getSensor, setSensor] = createSignal("")
  const [getMin, setMin] = createSignal(0)
  const [getHour, setHour] = createSignal(0)
  const [getDay, setDay] = createSignal(0)
  const [getState, setState] = createSignal("on")
  const [getBrightness, setBrightness] = createSignal(100)
  const [getSpeed, setSpeed] = createSignal(100)

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

      <Switches title="Schedule">
        <Button text='Get All Schedules' cb={getAllSchedules} />
        <Button text='Delete All Schedules' cb={deleteAllSchedules} />
      </Switches>

      <h1>Set Schedule</h1>
        <select onChange={(e) => {
            setSensor(e.target.value)
      }}>
            <option>-</option>
            <option>light</option>
            <option>pump</option>
        </select>
        <input type="text" placeholder="min" onChange={(e) => setMin(Number(e.target.value))}/>
        <input type="text" placeholder="hour" onChange={(e) => setHour(Number(e.target.value))}/>
        <input type="text" placeholder="day" onChange={(e) => setDay(Number(e.target.value))}/>
        <input type="text" placeholder="state" onChange={(e) => setState(e.target.value)}/>
        <input type="text" placeholder="brightness" onChange={(e) => setBrightness(Number(e.target.value))}/>
        <input type="text" placeholder="speed" onChange={(e) => setSpeed(Number(e.target.value))}/>
          <button onClick={() => {
            addSchedule(getSensor(), {
              minutes: getMin(),
              hour: getHour(),
              day: getDay(),
              state: getState(),
              brightness: getBrightness(),
              speed: getSpeed()
                })
            }}>
              Submit
          </button>

    </div>
  );
};

export default App;
