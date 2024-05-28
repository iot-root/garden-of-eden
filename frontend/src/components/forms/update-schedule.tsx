import { Button } from '@/components/ui/button';
import { TextField, TextFieldRoot } from '@/components/ui/textfield';
import { deleteScheduleById, updateSchedule } from '@/endpoints/schedule';
import { rangeValidator } from '@/root/libs/validators';
import { Checkbox } from '@/ui/checkbox/checkbox';
import { For, createSignal } from 'solid-js';
import { Col } from '../containers/col';
import Padding from '../containers/padding';
import { Row } from '../containers/row';
import { Card } from '../ui/card';
import SensorToggle from '../ui/toggle/toggle';
import { ErrorMessage } from './error-message';

export const UpdateSchedule = (props) => {
  const job = props.job;
  // days
  const [sun, setSun] = createSignal(job.day === 'Sunday');
  const [mon, setMon] = createSignal(job.day === 'Monday');
  const [tues, setTues] = createSignal(job.day === 'Tuesday');
  const [wed, setWed] = createSignal(job.day === 'Wednesday');
  const [thurs, setThurs] = createSignal(job.day === 'Thursday');
  const [fri, setFri] = createSignal(job.day === 'Friday');
  const [sat, setSat] = createSignal(job.day === 'Saturday');

  // time
  const [time, setTime] = createSignal(job.time);
  // const timeString = String(time()).split(':');
  // const [hour, setHour] = createSignal(timeString[0]);
  // const [min, setMin] = createSignal(timeString[1]);

  // lights
  const [lightsRun, setLightsRun] = createSignal(
    String(job.details).split(' ')[0] === 'Brightness:'
  );
  const [lightsDuration, setLightsDuration] = createSignal(0);
  const [lightsBrightness, setLightsBrightness] = createSignal(0);

  // pump
  const [pumpRun, setPumpRun] = createSignal(
    String(job.details).split(' ')[0] === 'Speed:'
  );
  const [pumpDuration, setPumpDuration] = createSignal(0);
  const [pumpSpeed, setPumpSpeed] = createSignal(0);

  // logs
  const [logTemp, setLogTemp] = createSignal(false);
  const [logHumidity, setLogHumidity] = createSignal(false);
  const [logPCBTemp, setLogPCBTemp] = createSignal(false);
  const [logCameras, setLogCameras] = createSignal(false);

  // form actions
  const onSubmit = async () => {
    const days = [sun(), mon(), tues(), wed(), thurs(), fri(), sat()];
    const countOfDays = days.filter((d) => d == true);
    if (countOfDays.length == 0) {
      console.error('Please select a day');
      return;
    }

    let timeString = time();
    if (!timeString) {
      console.error('Please select a time');
      return;
    }
    timeString = String(timeString).split(':');
    const mins = timeString[1];
    const hour = timeString[0];

    // TODO: improve logic, because you cant assign two different jobs the same id
    try {
      for (let i = 0; i < days.length; i++) {
        if (days[i]) {
          if (lightsRun()) {
            await updateSchedule('light', {
              id: job.id,
              minutes: Number(mins),
              hour: Number(hour),
              day: Number(i),
              state: 'on',
              brightness: Number(lightsBrightness()),
            });
          } else if (pumpRun()) {
            await updateSchedule('pump', {
              id: job.id,
              minutes: Number(mins),
              hour: Number(hour),
              day: Number(i),
              state: 'on',
              speed: Number(pumpSpeed()),
            });
          }
        }
      }
      await job.refetch().then(job.onClose());
    } catch (e) {
      console.error('Submission failed: ', e);
    }

    // TODO: create log schedule
  };

  const onDelete = async () => {
    await deleteScheduleById({ id: job.id });
    await props.refetch().then(props.onClose());
  };

  return (
    <Padding>
      <Card class="flex flex-col justify-start items-start min-w-[300px]">
        <div class="flex flex-col items-start mb-8">
          <p class="font-bold">Update Schedule</p>
          <p class="text-sm text-zinc-400">
            Change the details of this schedule.
          </p>
        </div>

        {/* days */}
        <Section title="Days">
          {[
            <div class="flex flex-row justify-between w-[80%]">
              <div>
                <Checkbox label="Monday" checked={mon()} onChange={setMon} />
                <Checkbox label="Tuesday" checked={tues()} onChange={setTues} />
                <Checkbox label="Wednesday" checked={wed()} onChange={setWed} />
                <Checkbox
                  label="Thursday"
                  checked={thurs()}
                  onChange={setThurs}
                />
              </div>

              <div>
                <Checkbox label="Friday" checked={fri()} onChange={setFri} />
                <Checkbox label="Saturday" checked={sat()} onChange={setSat} />
                <Checkbox label="Sunday" checked={sun()} onChange={setSun} />
              </div>
            </div>,
          ]}
        </Section>

        {/* time */}
        <Section title="Time">
          {[
            <Row>
              <TextFieldRoot onChange={setTime} required class="w-full mr-2">
                <TextField type="time" value={time()} />
              </TextFieldRoot>
            </Row>,
          ]}
        </Section>

        {/* Lights */}
        {lightsRun() ? (
          <Section title="Lights">
            <>
              <p class="font-light">Run</p>
              <SensorToggle
                checked={lightsRun()}
                onChange={() => setLightsRun(!lightsRun())}
              />
            </>

            <>
              <Col class="h-full">
                <p class="font-light">Duration</p>
                <ErrorMessage
                  validator={() => rangeValidator(lightsDuration(), 0, 59)}
                  message="Pick a value between 0 and 59."
                />
              </Col>
              <TextFieldRoot
                onChange={setLightsDuration}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(lightsDuration(), 1, 59) ? 'valid' : 'invalid'
                }
              >
                <TextField
                  type="number"
                  placeholder="mins"
                  value={lightsDuration()}
                />
              </TextFieldRoot>
            </>

            <>
              <Col class="h-full">
                <p class="font-light">Brightness</p>
                <ErrorMessage
                  validator={() => rangeValidator(lightsBrightness(), 0, 100)}
                  message="Pick a value between 0 and 100."
                />
              </Col>
              <TextFieldRoot
                onChange={setLightsBrightness}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(lightsBrightness(), 0, 100)
                    ? 'valid'
                    : 'invalid'
                }
              >
                <TextField
                  type="number"
                  placeholder="%"
                  value={lightsBrightness()}
                />
              </TextFieldRoot>
            </>
          </Section>
        ) : (
          ''
        )}

        {/* Pump */}
        {pumpRun() ? (
          <Section title="Pump">
            <>
              <Row class="w-full justify-between">
                <p class="font-light">Run</p>
                <SensorToggle
                  checked={pumpRun()}
                  onChange={() => setPumpRun(!pumpRun())}
                />
              </Row>
            </>
            <>
              <Col class="h-full">
                <p class="font-light">Duration</p>
                <ErrorMessage
                  validator={() => rangeValidator(pumpDuration(), 0, 59)}
                  message="Pick a value between 0 and 59."
                />
              </Col>
              <TextFieldRoot
                onChange={setPumpDuration}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(lightsDuration(), 1, 59) ? 'valid' : 'invalid'
                }
              >
                <TextField
                  type="number"
                  placeholder="mins"
                  value={pumpDuration()}
                />
              </TextFieldRoot>
            </>

            <>
              <Col class="h-full">
                <p class="font-light">Speed</p>
                <ErrorMessage
                  validator={() => rangeValidator(pumpSpeed(), 0, 100)}
                  message="Pick a value between 0 and 100."
                />
              </Col>

              <TextFieldRoot
                onChange={setPumpSpeed}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(pumpDuration(), 0, 100) ? 'valid' : 'invalid'
                }
              >
                <TextField type="number" placeholder="%" value={pumpSpeed()} />
              </TextFieldRoot>
            </>
          </Section>
        ) : (
          ''
        )}

        {/* Logs */}
        <Section title="Logs">
          <Row class="w-full justify-between">
            <p class="font-light">Temp</p>
            <SensorToggle
              check={logTemp()}
              onChange={() => setLogTemp(!logTemp())}
            />
          </Row>

          <Row class="w-full justify-between">
            <p class="font-light">Humidity</p>
            <SensorToggle
              check={logHumidity()}
              onChange={() => setLogHumidity(!logHumidity())}
            />
          </Row>

          <Row class="w-full justify-between">
            <p class="font-light">PCB Temp</p>
            <SensorToggle
              check={logPCBTemp()}
              onChange={() => setLogPCBTemp(!logPCBTemp())}
            />
          </Row>

          <Row class="w-full justify-between">
            <p class="font-light">Cameras</p>
            <SensorToggle
              check={logCameras()}
              onChange={() => setLogCameras(!logCameras())}
            />
          </Row>
        </Section>

        {/* Buttons */}
        <div class="flex flex-row justify-between w-full">
          <Button variant="destructive" onClick={onDelete}>
            Delete
          </Button>
          <Button onClick={onSubmit}>Save</Button>
        </div>
      </Card>
    </Padding>
  );
};

export const Section = (props) => {
  return (
    <Col class="mb-8 items-start w-full">
      <p class="font-medium mb-2">{props.title}</p>
      <Col class="w-full">
        <For each={props.children}>
          {(child) => {
            return (
              <Row class="justify-between w-full min-h-[40px]">{child}</Row>
            );
          }}
        </For>
      </Col>
    </Col>
  );
};
