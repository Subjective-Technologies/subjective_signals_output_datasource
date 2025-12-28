import time
from subjective_abstract_data_source_package.SubjectiveDataSource import SubjectiveDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger


class SubjectiveSignalsOutputDataSource(SubjectiveDataSource):
    connection_type = "Signals"
    connection_fields = ["strategy", "symbol"]
    icon_svg = "<svg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><circle cx='12' cy='12' r='9' fill='#2d6a4f'/><path d='M7 12h10' stroke='#ffffff' stroke-width='2'/></svg>"

    def get_icon(self):
        return self.icon_svg

    def get_connection_data(self):
        return {"connection_type": self.connection_type, "fields": list(self.connection_fields)}

    def _emit_result(self, result):
        if result is None:
            self.set_total_items(0)
            self.set_processed_items(0)
            return
        if isinstance(result, (list, tuple)):
            self.set_total_items(len(result))
            self.set_processed_items(0)
            for item in result:
                self.update(item)
                self.increment_processed_items()
            return
        self.set_total_items(1)
        self.set_processed_items(0)
        self.update(result)
        self.increment_processed_items()

    def fetch(self):
        start = time.perf_counter()
        if self.status_callback:
            self.status_callback(self.get_name(), "fetch_started")
        from com_goldenthinker_trade_database.TinyDbConnector import TinyDbConnector

        signals = TinyDbConnector.instance_for_signals().db.all()
        self._emit_result({"signals": signals})
        duration = time.perf_counter() - start
        self.set_total_processing_time(duration)
        self.set_fetch_completed(True)
        if self.progress_callback:
            self.progress_callback(self.get_name(), self.get_total_to_process(), self.get_total_processed(), self.estimated_remaining_time())
        if self.status_callback:
            self.status_callback(self.get_name(), "fetch_completed")
        BBLogger.log(f"Fetch completed for {self.get_name()}")
