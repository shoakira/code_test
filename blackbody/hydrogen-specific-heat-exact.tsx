import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const HydrogenSpecificHeatPlot = () => {
  // 最適化されたパラメータ
  const params = {
    midpoint: 150,
    width: 120,
    steepness: 3.5,
    maxValue: 2.42
  };
  
  // シグモイドモデル関数
  const smoothModel = (temp) => {
    // シグモイド関数
    const sigmoid = (x) => 1 / (1 + Math.exp(-x));
    
    // 中心点と幅を調整したシグモイド
    const normalizedTemp = (temp - params.midpoint) / params.width;
    const transitionFactor = sigmoid(normalizedTemp * params.steepness);
    
    // 1.5から最大値への滑らかな遷移
    return 1.5 + (params.maxValue - 1.5) * transitionFactor;
  };
  
  // グラフデータを生成
  const generateData = () => {
    const data = [];
    
    // 0Kから300Kまで1K刻みでデータポイントを生成
    for (let temp = 0; temp <= 300; temp += 1) {
      data.push({
        temperature: temp,
        specificHeat: smoothModel(temp)
      });
    }
    
    return data;
  };
  
  // 実験値の点データ
  const experimentalPoints = [
    { temperature: 0, specificHeat: 1.5 },
    { temperature: 50, specificHeat: 1.5 },
    { temperature: 75, specificHeat: 1.57 },
    { temperature: 100, specificHeat: 1.67 },
    { temperature: 125, specificHeat: 1.83 },
    { temperature: 150, specificHeat: 2.0 },
    { temperature: 175, specificHeat: 2.13 },
    { temperature: 200, specificHeat: 2.22 },
    { temperature: 225, specificHeat: 2.29 },
    { temperature: 250, specificHeat: 2.35 },
    { temperature: 275, specificHeat: 2.39 },
    { temperature: 300, specificHeat: 2.42 }
  ];
  
  const data = generateData();
  
  return (
    <div className="w-full h-96 p-4 bg-white">
      <h2 className="text-xl font-bold mb-4 text-center">水素のモル比熱と温度の関係（実験値）</h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          margin={{ top: 5, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid />
          <XAxis 
            type="number"
            dataKey="temperature"
            domain={[0, 300]}
            tickCount={7}
            label={{ value: '温度', position: 'insideBottom', offset: -5 }}
            ticks={[0, 50, 100, 150, 200, 250, 300]}
          />
          <YAxis 
            domain={[1.5, 2.5]} 
            label={{ value: 'C/R', angle: -90, position: 'insideLeft', offset: 10 }}
            ticks={[1.5, 2.0, 2.5]}
          />
          <Tooltip 
            formatter={(value) => [value.toFixed(2), 'C/R']}
            labelFormatter={(value) => `${value} K`}
          />
          
          {/* モデル曲線 - 太めの実線 */}
          <Line 
            data={data}
            type="monotone" 
            dataKey="specificHeat" 
            stroke="#000000" 
            strokeWidth={2}
            dot={false} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HydrogenSpecificHeatPlot;