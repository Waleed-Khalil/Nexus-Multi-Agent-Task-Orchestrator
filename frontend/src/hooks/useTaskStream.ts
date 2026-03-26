import { useCallback, useRef, useState } from "react";
import type { StreamEvent } from "../types";
import { streamTask } from "../utils/api";

export function useTaskStream() {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const startStream = useCallback((taskId: string) => {
    // Close existing stream
    if (esRef.current) {
      esRef.current.close();
    }
    setEvents([]);
    setIsStreaming(true);

    const es = streamTask(
      taskId,
      (raw) => {
        try {
          const parsed: StreamEvent = JSON.parse(raw.data);
          setEvents((prev) => [...prev, parsed]);

          if (parsed.event === "done" || parsed.event === "error") {
            setIsStreaming(false);
            es.close();
          }
        } catch {
          // Ignore unparseable events
        }
      },
      () => {
        setIsStreaming(false);
        es.close();
      },
    );

    esRef.current = es;
  }, []);

  const stopStream = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return { events, isStreaming, startStream, stopStream };
}
