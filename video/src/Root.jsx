import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';

const padrao = {tipo: 'short', fps: 30, largura: 1080, altura: 1920, duracao: 90, cenas: [], selo: '', audio: null, sons: []};

export const Root = () => (
  <Composition
    id="Nexus"
    component={Video}
    defaultProps={padrao}
    durationInFrames={90}
    fps={30}
    width={1080}
    height={1920}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.max(30, props.duracao),
      fps: props.fps,
      width: props.largura,
      height: props.altura,
    })}
  />
);
