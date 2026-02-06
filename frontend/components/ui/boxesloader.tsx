'use client';

import { CSSProperties, memo } from "react";
import styled, { keyframes } from "styled-components";
import { useMediaQuery } from "react-responsive";
import { darken } from "polished";

type Vector3 = [number, number, number];

type BoxTransform = [number, number];

interface AnimParam {
  start: Vector3;
  end: Vector3;
}

interface Colors {
  main: string;
  right: string;
  left: string;
  shadow: string;
}

interface ContainerProps {
  $size: number;
  $marginBottom: number;
}

interface BoxProps {
  $size: number;
  $transformOffsets: BoxTransform;
  $animation: AnimParam;
  $duration: number;
}

interface BoxesLoaderProps {
  className?: string;
  boxColor?: string;
  shadowColor?: string;
  duration?: number;
  size?: string;
  desktopSize?: string;
  mobileSize?: string;
}

const ANIMATIONS: AnimParam[] = [
  { start: [100, 100, 200], end: [0, 0, 0] },
  { start: [0, 0, 100], end: [100, 0, 0] },
  { start: [100, 100, 0], end: [100, 100, 100] },
  { start: [200, 200, 100], end: [0, 100, 100] },
];

const BOX_TRANSFORMS: BoxTransform[] = [
  [100, 0],
  [0, 100],
  [100, 100],
  [200, 0],
];

const createAnimation = (params: AnimParam) => keyframes`
  0% {
    transform: translate(${params.start[0]}%, ${params.end[0]}%);
  }
  50% {
    transform: translate(${params.start[1]}%, ${params.end[1]}%);
  }
  100% {
    transform: translate(${params.start[2]}%, ${params.end[2]}%);
  }
`;

const Container = styled.div<ContainerProps>`
  --size: ${({ $size }) => $size}px;
  height: calc(var(--size) * 2);
  width: calc(var(--size) * 3);
  position: relative;
  transform-style: preserve-3d;
  transform-origin: 50% 50%;
  margin-bottom: ${({ $marginBottom }) => $marginBottom}px;
  padding: 70px;
  transform: rotateX(60deg) rotateZ(45deg);
`;

const Box = styled.div<BoxProps>`
  --size: ${({ $size }) => $size}px;
  --duration: ${({ $duration }) => $duration}ms;
  width: var(--size);
  height: var(--size);
  position: absolute;
  top: 0;
  left: 0;
  transform-style: preserve-3d;
  transform: translate(
    ${({ $transformOffsets }) => $transformOffsets[0]}%,
    ${({ $transformOffsets }) => $transformOffsets[1]}%
  );
  animation: ${({ $animation }) => createAnimation($animation)} var(--duration)
    linear infinite;
`;

const Face = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
`;

const parseSize = (value?: string): number | undefined => {
  if (!value) return undefined;
  const result = Number.parseFloat(value);
  return Number.isFinite(result) ? result : undefined;
};

const buildFaceStyles = (colors: Colors): CSSProperties[] => [
  {
    top: 0,
    left: 0,
    background: colors.main,
    transform: "translateZ(calc(var(--size) / 2))",
  },
  {
    right: 0,
    background: colors.right,
    transform: "rotateY(90deg) translateZ(calc(var(--size) / 2))",
  },
  {
    background: colors.left,
    transform: "rotateX(-90deg) translateZ(calc(var(--size) / 2))",
  },
  {
    top: 0,
    left: 0,
    background: colors.shadow,
    transform: "translateZ(calc(var(--size) * -3))",
  },
];

const DEFAULT_SIZE = 64;

const BoxesLoaderComponent = ({
  className = "boxesloader",
  boxColor = "#812ca8ff",
  shadowColor = "#dbe3f4",
  duration = 800,
  size = "64",
  desktopSize = "",
  mobileSize = "",
}: BoxesLoaderProps) => {
  const isDesktopOrLaptop = useMediaQuery({ query: "(min-width: 1224px)" });
  const isTabletOrMobile = useMediaQuery({ query: "(max-width: 1224px)" });

  const baseSize = parseSize(size) ?? DEFAULT_SIZE;
  let computedSize = baseSize;

  if (isDesktopOrLaptop) {
    computedSize = parseSize(desktopSize) ?? baseSize * 2;
  } else if (isTabletOrMobile) {
    computedSize = parseSize(mobileSize) ?? baseSize;
  }

  const boxSize = (computedSize * 32) / 64;
  const marginBottom = (computedSize * 50) / 64;

  const colors: Colors = {
    main: boxColor,
    right: darken(0.15, boxColor),
    left: darken(0.05, boxColor),
    shadow: shadowColor,
  };

  const faceStyles = buildFaceStyles(colors);

  return (
    <Container className={className} $size={boxSize} $marginBottom={marginBottom}>
      {ANIMATIONS.map((animation, index) => (
        <Box
          key={`box-${index}`}
          $size={boxSize}
          $animation={animation}
          $duration={duration}
          $transformOffsets={BOX_TRANSFORMS[index]}
        >
          {faceStyles.map((style, faceIndex) => (
            <Face key={`box-${index}-face-${faceIndex}`} style={style} />
          ))}
        </Box>
      ))}
    </Container>
  );
};

const BoxesLoader = memo(BoxesLoaderComponent);

export default BoxesLoader;
