import { LineGraph } from '@/components/dataviews/line-graph';
import { GetLogs } from '@/endpoints/logs';
import { parseLogs } from '@/root/libs/parsers';
import {
  Match,
  Switch,
  createEffect,
  createResource,
  createSignal,
} from 'solid-js';
import { Skeleton } from '../ui/skeleton';

export const LogView = (props) => {
  const [logs, { refetch }] = createResource(
    async () => await GetLogs(props.sensor)
  );
  const [parsedLogsData, setParsedLogsData] = createSignal([]);
  const [parsedLogsLabels, setParsedLogsLabels] = createSignal([]);
  const [isParentFetching, setIsParentFetching] = createSignal(false);

  createEffect(() => {
    if (logs()) {
      const parsedLogs = parseLogs(logs());
      setParsedLogsData(parsedLogs[props.field]);
      setParsedLogsLabels(parsedLogs.timestamp);
    }
  });

  createEffect(() => {
    setIsParentFetching(props.isParentFetching);
    refetch();
  });

  return (
    <div class={props.class}>
      <Switch>
        <Match when={logs()}>
          <LineGraph
            isParentFetching={isParentFetching()}
            data={parsedLogsData()}
            labels={parsedLogsLabels()}
            title={props.title}
          />
        </Match>

        <Match when={logs.loading}>
          <Skeleton class="w-full h-[100px] mb-4" />
        </Match>
      </Switch>
    </div>
  );
};
