# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import pandas as pd
import numpy as np

result1 = {
            "type": None,
            "data": None
            }

class Resample1():
    """ Resample time serie frequency"""
    def __init__(self, freq='1H', how=None, fill=None, limit=None, how_quality=None):
        """ Initialize

        Args:
            freq (str): Offset Aliases sting (A=year,M=month,W=week,D=day,H=hour,T=minute,S=second; e.g.: 1H10T)
            how (str): sampling method ('mean','max','min',first','last','median','sum'), default is 'mean'
            fill (str): if not null it defines the method for filling no-data ('bfill'= backward fill or ‘ffill’=forward fill), default=None
            limit (int): if not null defines the maximum numbers of allowed consecutive no-data valuas to be filled
            how_quality (str): sampling method ('mean','max','min',first','last','median','sum') for observation quality index (default is like 'how')
        """
        self.freq = freq
        self.how = how
        self.fill = fill
        self.limit = limit
        self.how_quality = False

    def execute1(self, dataframe):
        """  Resample the data """
        
        # temp_oat = set()
        df = dataframe
        if self.how_quality:
            temp_oat = df.resample(rule=self.freq,how={'data': self.how, 'quality': self.how_quality},fill_method=self.fill, limit=self.limit)
        else:
            temp_oat = df.resample(rule=self.freq,how=self.how,fill_method=self.fill, limit=self.limit)

        return temp_oat
        
class Statistics():
    """ compute base statistics: count, min, max, mean, std, 25%, 50% 75 percentile"""

    def __init__(self, data=True, quality=False, tbounds=[None, None]):
        """ Initialize the class

        Args:
            data (bool): if True compute statistics of data (default is True)
            quality (bool): if True compute statistics of quality (default is False)
            tbounds (list): a list or tuple of string (iso856) with upper and lower time limits for statistic calculation.
                            bounds are closed bounds (t0 >= t <= t1)
        """
        self.quality = quality
        self.data = data
        self.tbounds = tbounds
    def execute(self, dataframe):
        """ Compute statistics """
        df=dataframe
        self.elab = {}

        if self.tbounds == [None, None] or self.tbounds is None:
            if self.data is True and self.quality is False:
                self.elab['data'] = df['data'].describe().to_dict()
            elif self.data is True and self.quality is True:
                self.elab['data'] = df.describe().to_dict()
            elif self.data is False and self.quality is True:
                self.elab['data'] = df['quality'].describe().to_dict()
            else:
                raise Exception("data and quality cannot be both False")
        else:
            if self.data is True and self.quality is False:
                self.elab['data'] = df.ix[self.tbounds[0]:self.tbounds[1]]['data'].describe().to_dict()
            elif self.data is True and self.quality is True:
                self.elab['data'] = df.ix[self.tbounds[0]:self.tbounds[1]].describe().to_dict()
            elif self.data is False and self.quality is True:
                self.elab['data'] = df.ix[self.tbounds[0]:self.tbounds[1]]['quality'].describe().to_dict()
            else:
                raise Exception("data and quality cannot be both False")
        # resdat = 'dict'
        resdata= self.elab
        return resdata

class DigitalFilter():
    """ """
    def __init__(self, fs, lowcut, highcut=0.0, order=5, btype='lowpass'):
        """bandpass Butterworth filter

        Args:
            lowcut (float): low cutoff frequency
            highcut (float): high cutoff frequency
            fs (float): sampling frequency
            order (int): the filter order
            btype (str): band type, one of ['lowpass', 'highpass', 'bandpass', 'bandstop']

        Returns:
            A new OAT object with filitered data
        """
        self.lowcut = int(lowcut)
        self.highcut = int(highcut)
        self.fs = fs
        self.order = order
        self.btype = btype

    def execute(self, dataframe):
        df=dataframe
        """ Apply bandpass Butterworth filter to an OAT object """
        try:
            from scipy.signal import butter, lfilter, lfilter_zi
        except:
            raise ImportError("scipy.signal module is required for this method")

        nyq = 0.5 * self.fs
        low = self.lowcut / nyq
        high = self.highcut / nyq
        b, a = butter(self.order, [low, high], btype=self.btype)
        #y = lfilter(b, a, oat.ts['data'])
        zi = lfilter_zi(b, a)
        y, zo = lfilter(b, a, df['data'], zi=zi * df['data'][0])

        #copy oat and return the modified copy
        df['data'] = y
        resdata=df
        return resdata

class Exceedance():
    """ """
    def __init__(self, values=None, perc=None, etu='days', under=False):
        """ Exceedance probability calculation

        Args:
            values (list): list of excedance values to calculate the excedance probability
            perc (list): list of exceedance probability to calculate the excedance values
            etu (string): excedance time unit, allowed ['seconds','minutes','hours','days','years'], default='days'
            under (bool): caluclate the probability for which values are exceeded (False) or are not exceeded (“True”)

        Returns:
            A list of (values,probability,time) tuples, output excedance time is returned according specified *etu* value
        """
        if values and not isinstance(values, (list, tuple)):
            raise TypeError("values must be a list")
        if not perc and isinstance(perc, (list, tuple)):
            raise TypeError("perc must be a list")
        if values is None and perc is None:
            raise IOError("one of values or perc list are required")

        if not etu in ['seconds', 'minutes', 'hours', 'days', 'years']:
            raise TypeError("etu accpted values are: 'seconds','minutes','hours','days','years'")

        self.values = values
        self.perc = perc
        self.etu = etu
        self.under = under
        self.prob = []
        self.time_f = []

    def execute1(self, dataframe):
        df = dataframe
        try:
            import scipy.stats as sp
        except:
            raise ImportError("scipy module is required for this method")

        if df.index.freq:
            freq = df.index.freq.delta.total_seconds()
        else:
            freq = (df.index[1] - df.index[0]).seconds
        # freq=600

        if self.etu == 'seconds':
            res = freq
        elif self.etu == 'minutes':
            res = freq / 60
        elif self.etu == 'hours':
            res = freq / 3600
        elif self.etu == 'days':
            res = freq / (3600 * 24)
        elif self.etu == 'years':
            res = freq / (365 * 3600 * 24)
        data = df["data"].dropna().values
        result1['type'] = "dict list"
        if self.values:
            for v in self.values:
                perc = sp.percentileofscore(data, v)
                if not self.under:
                    perc = 100 - perc
                self.prob.append(perc)
                self.time_f.append(df.size * res * (perc / 100))
            temp = np.column_stack([np.array(self.values), np.array(self.prob), np.array(self.time_f)])
        elif self.perc:
            self.vals = np.array(np.percentile(a=data, q=self.perc, axis=None))
            temp = np.column_stack([np.array(self.perc), np.array(self.vals)])
        result1['data'] = []
        for elem in temp:
            #print(elem)
            if len(elem) > 2:
                result1['data'].append({"value": elem[0], "percentage": elem[1], "frequency": elem[2]})
            else:
                result1['data'].append({"percentage": 100 - elem[0], "value": elem[1]})

        result1['type'] = 'dict list'
        # print(result2)
        return result1['data']

class Integrate():
    """ Integrate a time series using different methods """

    def __init__(self, periods=[(None, None)], tunit="seconds", factor=1, how='trapz', astext=False):
        """Perform integration of time series curve

        Args:
            periods (list): a list of tuples with upper and lower time limits for volumes computation.
            tunit (str): The time units of data employed by the time series, one of: 'seconds', 'minutes', 'hours', 'days', 'years'.
            factor (float): factor by which integrated volumes or masses are multiplied before storage
                generally used for unit conversion (e.g.: 0.0283168 will convert cubic feets to cubic meters)
            how (str): integration method, available methods are:
                * trapz - trapezoidal
                * cumtrapz - cumulative trapezoidal
                * simps - Simpson's rule
                * romb - Romberger's rule
            astext: define if dates has to be returned as text (True) or Timestamp (False). Default is False.

        Returns:
            a tuple of two oat.Sensor objects (baseflow,runoff)
        """

        integration_how = ['trapz', 'cumtrapz', 'simps', 'romb']
        if not how in integration_how:
            raise ValueError("integration mode %s not supported use one of: %s" % (how, integration_how))
        if not tunit in ['seconds', 'minutes', 'hours', 'days', 'years']:
            raise TypeError("tunit accpted values are: 'seconds','minutes','hours','days','years'")

        self.periods = periods
        self.factor = factor
        self.how = how
        self.astext = astext
        if tunit == 'seconds':
            self.res = 1
        elif tunit == 'minutes':
            self.res = 1 / 60
        elif tunit == 'hours':
            self.res = 1 / 3600
        elif tunit == 'days':
            self.res = 1 / (3600 * 24)
        elif tunit == 'years':
            self.res = 1 / (365 * 3600 * 24)

    def execute(self, dataframe):
        df=dataframe
        """ apply selected mode for hysep """
        try:
            from scipy import integrate
        except:
            raise ImportError("scipy is required from hyseo method")

        results = []
        tmin = df.index.min()
        tmax = df.index.max()
        for t in self.periods:
            t0 = t[0] or tmin
            t1 = t[1] or tmax
            rule = integrate.__getattribute__(self.how)

            result = rule(df['data'].loc[t0:t1].values, df.loc[t0:t1].index.astype(np.int64) / 10 ** 9).tolist()
            if self.astext:
                results.append({"from": "%s" % t0, "to": "%s" % t1, "value": result})
                #results.append(("%s" % t0, "%s" % t1, result * self.res * self.factor))
            else:
                results.append({"from": "%s" % t0, "to": "%s" % t1, "value": result})
                # results.append({"from": t0, "to": t1, "value": result})
                #results.append((t0, t1, result * self.res * self.factor))
        return results

class HydroGraph12():
    """ Class to assign constant weight values """

    def __init__(self, mode, alpha=0.98, bfl_max=0.50):
        """Perform hydrogram separation

        Args:
            mode (str): the method for hydrograph separation.
            Alleowed modes are:
            * TPDF: Two Parameter Digital Filter (Eckhardt, K., 2005. How to Construct Recursive Digital Filters
              for Baseflow Separation. Hydrological Processes, 19(2):507-515).
            * SPDF: Single Parameter Digital Filter (Nathan, R.J. and T.A. McMahon, 1990. Evaluation of Automated
              Techniques for Baseflow and Recession Analysis. Water Resources Research, 26(7):1465-1473).

        Returns:
            a tuple of two oat.Sensor objects (baseflow,runoff)
        """

        if not mode in ['TPDF', 'SPDF']:
            raise ValueError("stat parameter shall be one of: 'VAR','SD','CV','WT','SQRWT'")

        self.mode = mode
        self.alpha = alpha
        self.bfl_max = bfl_max

    def execute12(self,dataframe):
        df=dataframe
        """ apply selected mode for hysep """
        #if 'use' in oat.ts.columns:
            #del oat.ts['use']
        import copy
        flux = copy.deepcopy(df)
        base = copy.deepcopy(df)
#         return copy.deepcopy(self)
#         print df
        #print (base.ts.ix[0]['data'])
#         print flux
        base['quality'] = np.zeros(base['quality'].size)
        base['data'] = np.zeros(base['data'].size)
        runoff = base.copy()
        base.ix[0, 'data'] = flux.ix[0, 'data']

        #print (len(flux.ts.index))

        if self.mode == 'TPDF':
            a = (1 - self.bfl_max) * self.alpha
            b = (1 - self.alpha) * self.bfl_max
            c = (1 - self.alpha * self.bfl_max)
            for i in range(1, len(flux.index)):
                #base.ts.ix[i]['data'] = ((1 - self.bfl_max) * self.alpha * base.ts.ix[i - 1]['data']
                    #+ (1 - self.alpha) * self.bfl_max * flux.ts.ix[i]['data']) / (1 - self.alpha * self.bfl_max)
                base.ix[i, 'data'] = (a * base.ix[i - 1, 'data']
                    + b * flux.ix[i, 'data']) / c
                if base.ix[i, 'data'] > flux.ix[i, 'data']:
                    base.ix[i, 'data'] = flux.ix[i, 'data']
                runoff.ix[i, 'data'] = flux.ix[i, 'data'] - base.ix[i, 'data']

        elif self.mode == 'SPDF':
            a = (1 + self.alpha) / 2
            for i in range(1, len(flux.index)):
                #runoff.ts.ix[i]['data'] = (self.alpha * runoff.ts.ix[i - 1]['data']
                    #+ ((1 + self.alpha) / 2) * (flux.ts.ix[i]['data'] - flux.ts.ix[i - 1]['data']))
                runoff.ix[i, 'data'] = (self.alpha * runoff.ix[i - 1, 'data']
                    + a * (flux.ix[i, 'data'] - flux.ix[i - 1, 'data']))
                if runoff.ix[i, 'data'] < 0:
                    runoff.ix[i, 'data'] = 0
                if runoff.ix[i, 'data'] > flux.ix[i, 'data']:
                    runoff.ix[i, 'data'] = flux.ix[i, 'data']
                base.ix[i, 'data'] = flux.ix[i, 'data'] - runoff.ix[i, 'data']

        # base.name = "{}_base".format('base')
        # runoff.name = "{}_runoff".format('runoff')
        result1 = {
            "op": "Hydro Saparation",
            "base": [],
            "runoff":[]
        }
        result1['base'] = base
        result1['runoff']=runoff
        return result1

class SetDataValues1():
    """ Class to assign constant values """

    def __init__(self, value, vbounds=[(None, None)], tbounds=[(None, None)]):
        """Assign a constant value to the time series

        Args:
            value (float): the value to be assigned
            vbounds (list): a list of tuples with upper and lower value limits for assignment.
                bounds are closed bounds (min >= x <= max)
                e.g: [(None,0.2),(0.5,1.5),(11,None)] will apply:
                if data is lower then 0.2 # --> (None,0.2)
                or data is between 0.5 and 1.5 # --> (0.5,1.5)
                or data is higher then 11 # --> (11,None)
            tbounds (list): a list of tuples with upper and lower time limits for assignment.
                bounds are closed bounds (t0 >= t <= t1)

        Returns:
            a new oat.Sensor object with assigned constant value based on conditions
        """
        self.value = value

        if not vbounds:
            self.vbounds = [(None, None)]
        else:
            self.vbounds = vbounds

        if not tbounds:
            self.tbounds = [(None, None)]
        else:
            self.tbounds = tbounds

    def execute(self, dataframe):
        """ aaply statistics acording to conditions """
        # df=dataframe
        import copy
        df=copy.deepcopy(dataframe)
        tmp=copy.deepcopy(dataframe)
        #apply the value to all observations
        #Here is df placed of df.loc['data']
        if self.vbounds == [(None, None)] and self.tbounds == [(None, None)]:
            df.loc['data'] = df['data'].apply(lambda d: self.value)
            resdata=tmp
        #apply value to combination of time intervals and vaue intervals (periods and tresholds)
        elif self.tbounds and self.vbounds:
            tmin = df.index.min()
            tmax = df.index.max()
            vmin = df['data'].min()
            vmax = df['data'].max()
            for t in self.tbounds:
                t0 = t[0] or tmin
                t1 = t[1] or tmax
                for v in self.vbounds:
                    v0 = v[0] or vmin
                    v1 = v[1] or vmax
                    df.loc[(df.index >= t0) & (df.index <= t1) & (df['data'] >= v0) & (df['data'] <= v1),'data'] = self.value    
            resdata=df

        return resdata

class  QualityStat():
    """ Class to assign constant values """

    def __init__(self, value, vbounds=[(None, None)], tbounds=[(None, None)], statflag='WT'):
        """Assign a constant value to the time series

        Args:
            value (float): the value to be assigned
            vbounds (list): a list of tuples with upper and lower value limits for assignment.
                bounds are closed bounds (min >= x <= max)
                e.g: [(None,0.2),(0.5,1.5),(11,None)] will apply:
                if data is lower then 0.2 # --> (None,0.2)
                or data is between 0.5 and 1.5 # --> (0.5,1.5)
                or data is higher then 11 # --> (11,None)
            tbounds (list): a list of tuples with upper and lower time limits for assignment.
                bounds are closed bounds (t0 >= t <= t1)

        Returns:
            a new oat.Sensor object with assigned constant value based on conditions
        """
        if not statflag in ['VAR', 'SD', 'CV', 'WT', 'SQRWT']:
            raise ValueError("stat parameter shall be one of: 'VAR','SD','CV','WT','SQRWT'")

        self.value = value
        self.statflag = statflag

        if not vbounds:
            self.vbounds = [(None, None)]
        else:
            self.vbounds = vbounds

        if not tbounds:
            self.tbounds = [(None, None)]
        else:
            self.tbounds = tbounds

    def execute(self, dataframe):
        """ aaply statistics acording to conditions """
        df=dataframe
        #apply the vaue to all observations
        if self.vbounds == [(None, None)] and self.tbounds == [(None, None)]:
            df['quality'] = df['quality'].apply(lambda d: self.value)
            
        #apply value to combination of time intervals and vaue intervals (periods and tresholds)
        elif self.tbounds and self.vbounds:
            tmin = df.index.min()
            tmax = df.index.max()
            vmin = df['data'].min()
            vmax = df['data'].max()
            for t in self.tbounds:
                t0 = t[0] or tmin
                t1 = t[1] or tmax
                for v in self.vbounds:
                    v0 = v[0] or vmin
                    v1 = v[1] or vmax
                    df.loc[
                                (df.index >= t0) & (df.index <= t1)
                                & (df['data'] >= v0) & (df['data'] <= v1),
                                'quality'
                            ] = self.value

        # df.statflag = self.statflag
        resdata=df
        return resdata

class Fill1():
    """ """
    def __init__(self, fill=None, limit=None):
        """Different methods for No data filling

        Args:
            fill (str): if not null it defines the method for filling no-data optional are:
                * 'bfill' = backward fill
                * ‘ffill’ = forward fill
                * 'time' = interpolate proportional to time distance
                * 'spline' = use spline interpolation
                * 'linear' = linear interpolation
                * 'quadratic'= quadratic interpolation
                * 'cubic'= cucbic interpolation
            limit (int): if method is ffill or bfill when not null defines the maximum numbers of allowed consecutive no-data valuas to be filled
        """
        self.fill = fill
        self.limit = limit
    def execute(self, dataframe):
        df=dataframe
        """ Fill no-data"""

        if self.fill in ['bfill', 'ffill']:
            temp_oat1 = df.fillna(method=self.fill, limit=self.limit)
        if self.fill in ['time', 'spline', 'polynomial', 'linear', 'quadratic', 'cubic']:
            temp_oat1 = df.interpolate(method=self.fill, limit=self.limit)
        return temp_oat1

class HargreavesETo1():
    """ """
    def __init__(self):
        self.prob = []
        self.time_f = []
    def execute1(self, dataframe):
        """ execute method """
        df = dataframe
        temp_oat = df.groupby(pd.TimeGrouper(freq='D')).agg({'data': lambda x: (0.0023 * (x.mean() + 17.8) * (x.max() - x.min()) ** 0.5),'quality': np.min})
        return temp_oat

class HydroIndices1():
    """ class to calculate hydrologic indices"""

    __htype__ = ["MA", "ML", "MH", "FL", "FH", "DL", "DH", "TA", "TL", "TH", "RA"]

    def __init__(self, htype, code1, period=None, flow_component=False, stream_classification=False, median=False, drain_area=None):
        """peak flow periods extraction

        Args:
            htype (str): alphanumeric code, one of [MA,ML,MH,FL,FH,DL,DH,TA,TL,TH,RA]
            code (int): code that jointly with htype determine the indiced to calculate (see TSPROC HYDROLOGIC_INDECES Table 3-2, page 90)
            period (tuple): tuple of two elements indicating the BEGIN and END of datetimes records to be used.
            flow_component (str): Specify the hydrologic regime as defined in Olden and Poff (2003).
                One of ["AVERAGE_MAGNITUDE", "LOW_FLOW_MAGNITUDE", "HIGH_FLOW_MAGNITUDE", "LOW_FLOW_FREQUENCY,
                HIGH_FLOW_FREQUENCY", "LOW_FLOW_DURATION", "HIGH_FLOW_DURATION", "TIMING", "RATE_OF_CHANGE"]
            stream_classification (str): Specify the hydrologic regime as defined in Olden and Poff (2003).
                One of ["HARSH_INTERMITTENT", "FLASHY_INTERMITTENT", "SNOWMELT_PERENNIAL", "SNOW_RAIN_PERENNIAL", "
                    GROUNDWATER_PERENNIAL", "FLASHY_PERENNIAL", "ALL_STREAMS"]
            median (bool): Requests that indices that normally report the mean of some other sumamry statistic to instead report the median value.
            drain_area (float): the gauge area in m3

        Returns:
            A list of oat objects with a storm hydrograph each, they will be named "seriesName+suffix+number"
            (e.g.: with a series named "TEST" and a suffic "_hyevent_N" we will have: ["TEST_hyevent_N1, TEST_hyevent_N2, ...]
        """

        if not htype in self.__htype__:
            raise ValueError("htype shall be in %s" % self.__htype__)

        self.htype = htype
        self.code1 = code1
        self.period = period
        self.flow_component = flow_component
        self.stream_classification = stream_classification
        self.median = median
        self.drain_area = drain_area

    def execute(self, dataframe):
        df=dataframe
        """ calculate peak hydrographs """
        
        if self.htype == "MA":
            #raise Exception(str(oat.ts))
            if not df.index.freq or df.index.freq.delta.total_seconds() != 60 * 60 * 24:
                tmp_oat = Resample1(freq='1D', how='mean').execute1(df)
            else:
                tmp_oat = df

            if self.code1 == 1:
                # Mean of the daily mean flow values for the entire flow record
                value = tmp_oat.mean()['data']
            elif self.code1 == 2:
                # Median of the daily mean flow values for the entire flow record.
                value = tmp_oat.median()['data']
            elif self.code1 == 3:
                # Mean (or median) of the coefficients of variation (standard deviation/mean) for each year.
                # Compute the coefficient of variation for each year of daily flows. Compute the mean of the annual coefficients of variation
                l = [v.std()[0] / v.mean()[0] for a, v in tmp_oat.groupby(tmp_oat.index.year)]
                value = sum(l) / float(len(l))
            elif self.code1 == 4:
                #Standard deviation of the percentiles of the logs of the entire flow record divided by the mean of percentiles of the logs.
                #Compute the log10 of the daily flows for the entire record.
                #Compute the 5th, 10th, 15th, 20th, 25th, 30th, 35th, 40th, 45th, 50th, 55th, 60th, 65th, 70th,
                #75th, 80th, 85th, 90th, and 95th percentiles for the logs of the entire flow record.
                #Percentiles are computed by interpolating between the ordered (ascending) logs of the flow values.
                #Compute the standard deviation and mean for the percentile values. Divide the standard deviation by the mean.
                q = np.log(tmp_oat["data"]).quantile(
                    [.05, .10, .15, .20, .25, .30, .35, .40, .45, .50,
                         .55, .60, .65, .70, .75, .80, .85, .90, .95])
                value = q.std() / q.mean()
            elif self.code1 == 5:
                #The skewness of the entire flow record is computed as the mean for the entire flow record (MA1)
                #divided by the median (MA2) for the entire flow record.
                value = tmp_oat.mean()['data'] / tmp_oat.median()['data']
            elif self.code1 == 6:
                #Range in daily flows is the ratio of the 10-percent to 90-percent exceedance values for the entire flow record.
                #Compute the 5-percent to 95-percent exceedance values for the entire flow record.
                #Exceedance is computed by interpolating between the ordered (descending) flow values.
                #Divide the 10-percent exceedance value by the 90-percent value.
                #exc = oat.process(ExceedanceProbability([4, 6, 10],etu='days')))
                exc = Exceedance(perc=[10, 90]).execute1(tmp_oat)
                value = exc[0]['value'] / exc[1]['value']
            elif self.code1 == 7:
                #Range in daily flows is the ratio of the 20-percent to 80-percent exceedance values for the entire flow record.
                exc = Exceedance(perc=[20,80]).execute1(tmp_oat)
                value = exc[0]['value'] / exc[1]['value']
            elif self.code1 == 8:
                #Range in daily flows is the ratio of the 25-percent to 75-percent exceedance values for the entire flow record.
                exc = Exceedance(perc=[25,75]).execute1(tmp_oat)
                value = exc[0]['value'] / exc[1]['value']
            elif self.code1 == 9:
                #Spread in daily flows is the ratio of the difference between the 90th and 10th percentile of the logs of the
                #flow data to the log of the median of the entire flow record.
                #Compute the log10 of the daily flows for the entire record.
                #Compute the 5th, 10th, 15th, 20th, 25th, 30th, 35th, 40th, 45th, 50th, 55th, 60th, 65th, 70th, 75th, 80th,
                #85th, 90th, and 95th percentiles for the logs of the entire flow record.
                #Percentiles are computed by interpolating between the ordered (ascending) logs of the flow values.
                #Compute MA9 as (90th –10th) /log10(MA2).
                q = np.log10(tmp_oat["data"]).quantile([.10, .90])
                value = (q[0.10] - q[0.90]) / np.log10(tmp_oat.median()['data'])
            elif self.code1 == 10:
                #Spread in daily flows is the ratio of the difference between the 80th and 20th percentile of the logs of the
                #flow data to the log of the median of the entire flow record.
                q = np.log10(tmp_oat["data"]).quantile([.20, .80])
                value = (q[0.20] - q[0.80]) / np.log10(tmp_oat.median()['data'])
            elif self.code1 == 11:
                #Spread in daily flows is the ratio of the difference between the 25th and 75th percentile of the logs of the
                #flow data to the log of the median of the entire flow record.
                q = np.log10(tmp_oat["data"]).quantile([.25, .75])
                value = (q[0.25] - q[0.75]) / np.log10(tmp_oat.median()['data'])
            elif self.code1 in range(12, 24):
                #Means (or medians) of monthly flow values. Compute the means for each month over the entire flow record.
                #For example, MA12 is the mean of all January flow values over the entire record.
                month_num = self.code1 - 11
                b = Resample1(freq='1M', how='mean').execute1(tmp_oat)
                try:
                    m = b.groupby(b.index.month).get_group(month_num)
                    v = m.mean()[0]
                except KeyError:
                    v = None
                value = v
            elif self.code1 in range(24, 36):
                #Variability (coefficient of variation) of monthly flow values.
                #Compute the standard deviation for each month in each year over the entire flow record.
                #Divide the standard deviation by the mean for each month. Average (or take median of) these values for each month across all years.
                month_num = self.code1 - 23
                #b = tmp_oat.process(Resample(freq='1M', how='std'))
                m = df.groupby([df.index.year, df.index.month]).agg([np.mean, np.std])  # .dropna()
                try:
                    cov = (m.xs(month_num, level=1)['data']['std'] / m.xs(month_num, level=1)['data']['mean']).mean()
                except KeyError:
                    cov = None
                value = cov
            elif self.code1 == 36:
                m = df.groupby([df.index.year, df.index.month]).agg([np.mean])
                value = (m.max()[0] - m.min()[0]) / m.median()[0]
            elif self.code1 == 37:
                m = df.groupby([df.index.year, df.index.month]).agg([np.mean])
                q = m.quantile([.25, .75])
                value = (q.ix[0.25][0] - q.ix[0.75][0]) / m.median()[0]
            elif self.code1 == 38:
                m = df.groupby([df.index.year, df.index.month]).agg([np.mean])
                q = m.quantile([.10, .90])
                value = (q.ix[0.10][0] - q.ix[0.90][0]) / m.median()[0]
            elif self.code1 == 39:
                m = df.groupby([df.index.year, df.index.month]).agg([np.mean])
                value = (m.std()[0] * 100) / m.mean()[0]
            elif self.code1 == 40:
                m = df.groupby([df.index.year, df.index.month]).agg([np.mean])
                value = (m.mean()[0] - m.median()[0]) / m.median()[0]
            elif self.code1 == 41:
                if self.drain_area is None:
                    raise ValueError("drain_area must be defined to calculate this indice!")
                m = df.groupby([df.index.year]).agg([np.mean])
                value = (m.mean()[0] - m.median()[0]) / self.drain_area
            elif self.code1 == 42:
                m = df.groupby([df.index.year]).agg([np.mean])
                value = (m.max()[0] - m.min()[0]) / m.median()[0]
            elif self.code1 == 43:
                m = df.groupby([df.index.year]).agg([np.mean])
                q = m.quantile([.25, .75])
                value = (q.ix[0.25][0] - q.ix[0.75][0]) / m.median()[0]
            elif self.code1 == 44:
                m = df.groupby([df.index.year]).agg([np.mean])
                q = m.quantile([.10, .90])
                value = (q.ix[0.10][0] - q.ix[0.90][0]) / m.median()[0]
            elif self.code1 == 45:
                m = df.groupby([df.index.year]).agg([np.mean])
                value = (m.mean()[0] - m.median()[0]) / m.median()[0]
            else:
                raise ValueError("the code number %s is not defined!" % self.code1)

            return value

class HydroEvents12():
    """ class to calculate portion of time series associated with peak flow events"""

    def __init__(self, rise_lag, fall_lag, window=1, min_peak=0, suffix="_event_N", period=None):
        """peak flow periods extraction

        Args:
            rise_lag (float): The number of days prior to the peak to include in the event hydrograph.
            fall_lag (float): The number of days following the peak to include in the event hydrograph.
            window (int): Minimum time between successive peaks, in days.
            min_peak (float): Minimum value for a peak.
            suffix (string): The name of the time series on which statistical calculations will be carried out.
            period (tuple): tuple of two elements indicating the BEGIN and END of datetimes records to be used in peak extraction.

        Returns:
            A list of oat objects with a storm hydrograph each, they will be named "seriesName+suffix+number"
            (e.g.: with a series named "TEST" and a suffic "_hyevent_N" we will have: ["TEST_hyevent_N1, TEST_hyevent_N2, ...]
        """
        self.rise_lag = rise_lag
        self.fall_lag = fall_lag
        self.window = window
        self.min_peak = min_peak
        self.suffix = suffix
        self.period = period

    def execute12(self, dataframe):
        """ aaply statistics acording to conditions """
        df=dataframe
        """ calculate peak hydrographs """
        try:
            from datetime import timedelta as dttd
            from scipy.signal import argrelmax
        except:
            raise ImportError("scipy module is required for this method")

        #win_stps = int(dttd(days=self.window) / oat.ts.index.freq.delta)
        # da=self.window
        win_dt = dttd(days=self.window)

        if self.period:
            signal = df[self.period[0]:self.period[1]]['data'].values
        else:
            signal = df['data'].values

        if not self.min_peak:
            self.min_peak = min(signal)

        #detect the local maxima above the setted treshold
        idx = argrelmax(np.clip(signal, self.min_peak, signal.max()))

        times = []
        vales = []
        index = idx[0].tolist()
        for i in range(len(index)):
            times.append(df.iloc[[index[i]]].index[0].to_datetime())
            vales.append(df.iloc[index[i]]['data'])
            #print(i, index[i], times[i], vales[i])

        events_idx = []

        while index != [None] * len(index):
            #detect the index of the max value
            imax = max(list(range(len(vales))), key=vales.__getitem__)
            iloc = None
            #find local maxima in range and opportunately set to None
            for i in range(len(index)):
                if (times[i] is not None) and (i != imax) and (abs(times[i] - times[imax]).total_seconds() < win_dt.total_seconds()):
                    #print(times[i], times[imax], abs(times[i] - times[imax]).total_seconds(), win_dt.total_seconds())
                    if vales[i] < vales[imax]:
                        times[i] = None
                        vales[i] = None
                        index[i] = None
            iloc = index[imax]
            index[imax] = None
            vales[imax] = None
            times[imax] = None
            if iloc is not None:
                events_idx.append(iloc)

        tsl = []
        for i in events_idx:
#             temp_oat.name = temp_oat.name + self.suffix + "%s" % (len(tsl) + 1)

            st = df.iloc[[i]].index[0].to_datetime() - pd.DateOffset(days=self.rise_lag)
            en = df.iloc[[i]].index[0].to_datetime() + pd.DateOffset(days=self.fall_lag)

            temp_oat = df[st:en]
            tsl.append(temp_oat)
        resdata=tsl
        # resdata=signal
        return resdata
