-- Event trigger to notify API layer on schema changes

CREATE OR REPLACE FUNCTION notify_ddl_change()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
BEGIN
  -- We just notify the channel 'ddl_events'
  PERFORM pg_notify('ddl_events', 'schema_changed');
END;
$$;

CREATE EVENT TRIGGER ddl_change_trigger
ON ddl_command_end
EXECUTE FUNCTION notify_ddl_change();
