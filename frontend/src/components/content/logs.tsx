import { CaptureSensors } from '@/endpoints/logs';
import { H1 } from '@/typography/heading';
import { Match, Switch, createSignal } from 'solid-js';
import { Oval } from 'solid-spinner';
import Padding from '../containers/padding';
import { LogView } from '../dataviews/log-view';
import { Add } from '../ui/add';

export const Logs = () => {
  const [isFetching, setIsFetching] = createSignal(false);

  const handleOnClick = async () => {
    setIsFetching(true);
    await CaptureSensors();
    setIsFetching(false);
  };

  return (
    <Padding>
      <div class="flex flex-row justify-between items-center mb-4">
        <H1>Log</H1>
        <Switch>
          <Match when={!isFetching()}>
            <button onClick={handleOnClick}>
              <Add label="Add" />
            </button>
          </Match>
          <Match when={isFetching()}>
            <Oval color="gray" />
          </Match>
        </Switch>
      </div>

      <div class="lg:grid lg:grid-cols-2 2xl:grid-cols-3 gap-4">
        <LogView
          isParentFetching={isFetching()}
          sensor="distance"
          field="value"
          title="Water Level cm"
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="temperature"
          field="value"
          title={'Temperature \u00B0C'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="humidity"
          field="value"
          title={'Humidity %'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="light"
          field="value"
          title={'Brightness %'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="pcb-temp"
          field="value"
          title={'PCB Temp. \u00B0C'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="pump/speed"
          field="value"
          title={'Pump Speed %'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="pump/stats"
          field="power"
          title={'Power W'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="pump/stats"
          field="bus_current"
          title={'Bus Current A'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="pump/stats"
          field="bus_voltage"
          title={'Bus Voltage V'}
        />
        <LogView
          isParentFetching={isFetching()}
          sensor="pump/stats"
          field="shunt_voltage"
          title={'Shunt Voltage A'}
        />
      </div>
    </Padding>
  );
};
