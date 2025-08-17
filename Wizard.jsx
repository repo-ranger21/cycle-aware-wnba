import React, { useState } from "react";
import styled from "styled-components";

const Stepper = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const StepDot = styled.div`
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: ${props => props.active ? "#2761d6" : "#ccc"};
  border: ${props => props.active ? "2px solid #2761d6" : "none"};
  transition: background 0.2s;
`;

const Form = styled.form`
  margin-bottom: 1rem;
`;

const Field = styled.div`
  margin-bottom: 1.25rem;
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  margin-bottom: 0.3rem;
`;

const Input = styled.input`
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #bbb;
  width: 100%;
`;

const Tooltip = styled.span`
  display: inline-block;
  margin-left: 0.4em;
  color: #2761d6;
  cursor: pointer;
  font-size: 1.1em;
  position: relative;
  &:hover::after {
    content: attr(data-tip);
    position: absolute;
    left: 1.2em;
    background: #fff9c4;
    color: #333;
    padding: 0.4em 0.8em;
    border-radius: 6px;
    border: 1px solid #eee;
    font-size: 0.95em;
    white-space: pre;
    z-index: 5;
  }
`;

const Nav = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 1em;
`;

const Button = styled.button`
  padding: 0.5em 1.25em;
  border-radius: 6px;
  border: none;
  background: #2761d6;
  color: white;
  font-weight: 600;
  cursor: pointer;
  &:disabled {
    background: #ddd;
    color: #888;
    cursor: not-allowed;
  }
`;

const PredictionBox = styled.div`
  padding: 1em;
  background: #e7f0ff;
  border-radius: 8px;
  margin-top: 1em;
  font-size: 1.1em;
`;

function Wizard() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    periodStart: "",
    flowIntensity: "",
    cycleLength: "",
    hrv: "",
    sleep: "",
    hydration: ""
  });

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function nextStep() {
    if (step < 3) setStep(step + 1);
  }
  function prevStep() {
    if (step > 1) setStep(step - 1);
  }

  // Satirical predictions
  function getPrediction() {
    // These are mock/satirical outputs for demonstration
    const points = Math.round(Math.random() * 15 + 5);
    const betRec = Math.random() > 0.5 ? "Fade the cramps, bet the over 🏀" : "Monitor hydration, bet the under 💧";
    const hormonalMACD = Math.random() > 0.5 ? "Bullish—Estrogen surge detected 📈" : "Bearish—Progesterone cycle incoming 📉";
    const crampCast = Math.random() > 0.5 ? "High CrampCast™ risk, hydrate!" : "Low CrampCast™ risk, full speed ahead!";
    return { points, betRec, hormonalMACD, crampCast };
  }

  const prediction = step === 3 ? getPrediction() : {};

  return (
    <>
      <Stepper aria-label="Wizard Progress">
        {[1, 2, 3].map(n => (
          <StepDot key={n} active={step === n} />
        ))}
      </Stepper>

      <Form>
        {step === 1 && (
          <>
            <Field>
              <Label htmlFor="periodStart">
                Period Start Date
                <Tooltip data-tip="The first day of your cycle. For civic-grade clarity, use ISO format.">ⓘ</Tooltip>
              </Label>
              <Input
                type="date"
                id="periodStart"
                name="periodStart"
                value={form.periodStart}
                onChange={handleChange}
                aria-label="Period Start Date"
              />
            </Field>
            <Field>
              <Label htmlFor="flowIntensity">
                Flow Intensity
                <Tooltip data-tip="Satirical overlay: Use your best civic-grade guess.">💧</Tooltip>
              </Label>
              <Input
                type="number"
                id="flowIntensity"
                name="flowIntensity"
                min="1"
                max="10"
                value={form.flowIntensity}
                onChange={handleChange}
                aria-label="Flow Intensity"
                placeholder="1 (light) - 10 (heavy)"
              />
            </Field>
            <Field>
              <Label htmlFor="cycleLength">
                Cycle Length (days)
                <Tooltip data-tip="Standard is 28, but life is not a textbook.">📅</Tooltip>
              </Label>
              <Input
                type="number"
                id="cycleLength"
                name="cycleLength"
                min="20"
                max="40"
                value={form.cycleLength}
                onChange={handleChange}
                aria-label="Cycle Length"
              />
            </Field>
          </>
        )}

        {step === 2 && (
          <>
            <Field>
              <Label htmlFor="hrv">
                HRV (Heart Rate Variability)
                <Tooltip data-tip="CrampCast™: Too low, risk of cramps; too high, risk of hype.">❤️</Tooltip>
              </Label>
              <Input
                type="number"
                id="hrv"
                name="hrv"
                value={form.hrv}
                onChange={handleChange}
                aria-label="HRV"
                placeholder="e.g. 50"
              />
            </Field>
            <Field>
              <Label htmlFor="sleep">
                Sleep (hours)
                <Tooltip data-tip="HormonalMACD™: Sleep is the best bet of all.">🛌</Tooltip>
              </Label>
              <Input
                type="number"
                id="sleep"
                name="sleep"
                value={form.sleep}
                onChange={handleChange}
                aria-label="Sleep Hours"
                placeholder="e.g. 7"
              />
            </Field>
            <Field>
              <Label htmlFor="hydration">
                Hydration Proxy
                <Tooltip data-tip="Satirical overlay: Gatorade color index, civic-grade edition.">🥤</Tooltip>
              </Label>
              <Input
                type="text"
                id="hydration"
                name="hydration"
                value={form.hydration}
                onChange={handleChange}
                aria-label="Hydration Proxy"
                placeholder="e.g. Clear"
              />
            </Field>
          </>
        )}

        {step === 3 && (
          <PredictionBox aria-label="Prediction Output">
            <strong>Prediction:</strong>
            <br />
            <span>Points: <b>{prediction.points}</b></span>
            <br />
            <span>Bet Recommendation: {prediction.betRec}</span>
            <br />
            <span>HormonalMACD™: {prediction.hormonalMACD}</span>
            <br />
            <span>CrampCast™: {prediction.crampCast}</span>
            <br />
            <Tooltip data-tip="Disclaimer: For entertainment, not medical or betting advice.">🛈</Tooltip>
          </PredictionBox>
        )}
      </Form>
      <Nav>
        <Button type="button" onClick={prevStep} disabled={step === 1}>Back</Button>
        <Button type="button" onClick={nextStep} disabled={step === 3}>Next</Button>
      </Nav>
    </>
  );
}

export default Wizard;