# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.


from ..core import BaseFuture, async, return_
from ..core.async_task import AsyncTask


class ActivityFuture(BaseFuture):

    def __init__(self, future, activity_task_handler, activity_id):
        """

        :param future:
        :type future: Future
        :param activity_task_handler:
        :type activity_task_handler: awsflow.decider.activity_task_handler.ActivityTaskHandler
        :param activity_id:
        :type activity_id: str
        :return:
        """
        super(ActivityFuture, self).__init__()

        self._future = future
        self._activity_task_handler = activity_task_handler
        self._activity_id = activity_id
        self._cancellation_future = None  # may be set to a Future if cancel was requested

        task = AsyncTask(self._future_callback, (future,),
                         name=self._future_callback.__name__)
        task.cancellable = False
        future.add_task(task)

    def _future_callback(self, future):
        if self.done():
            return

        if future.exception() is not None:
            self.set_exception(future.exception(),
                               future.traceback())
        else:
            self.set_result(future.result())

        if self._cancellation_future is not None:
            self._cancellation_future.set_result(None)

    def cancel(self):
        """

        :return: Cancellation future
        :rtype: awsflow.Future
        """
        self._cancellation_future = self._activity_task_handler.request_cancel_activity_task(self, self._activity_id)
        return self._cancellation_future
