"""
Module containing `ray` integrations
"""
try:
    import ray
except ImportError:
    raise ImportError('To use this module you have to install ray Python package')
from tqdm.auto import tqdm

from ..eoexecution import EOExecutor, _ProcessingType


class RayExecutor(EOExecutor):

    def run(self, return_results=False):
        """ Runs the executor using the Ray Cluster.

        :param return_results: If `True` this method will return a list of all results of the execution. Note that
            this might exceed the available memory. By default this parameter is set to `False`.
        :type: bool
        :return: If `return_results` is set to `True` it will return a list of results, otherwise it will return `None`
        :rtype: None or list(eolearn.core.WorkflowResults)
        """
        # TODO: perhaps try initializing ray with a given number of workers?
        return super().run(workers=None, multiprocess=True, return_results=return_results)

    @staticmethod
    def _get_processing_type(*args, **kwargs):
        return _ProcessingType.RAY

    @staticmethod
    def _run_execution(processing_args, *args, **kwargs):
        """ Runs ray execution
        """
        workflow_executor = ray.remote(RayExecutor._execute_workflow)
        futures = [workflow_executor.remote(workflow_args) for workflow_args in processing_args]

        # Using tqdm directly on futures causes memory problems and is not accurate
        def progress_bar_iterator(futures):
            while futures:
                done, futures = ray.wait(futures, num_returns=1)
                yield

        for _ in tqdm(progress_bar_iterator(futures), total=len(futures)):
            pass

        return ray.get(futures)