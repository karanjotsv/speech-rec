import wave

obj = wave.open('hi.wav', 'rb')

print('channels', obj.getnchannels())
print('sample width', obj.getsampwidth())

print('frame rate', obj.getframerate())
print('frames', obj.getnframes())

print('parameters', obj.getparams())

t_audio = obj.getnframes() / obj.getframerate()
# print(t_audio)

frames = obj.readframes(-1)
# print(type(frames), type(frames[0]), len(frames)/2)

obj.close()

obj_new = wave.open('hi_new.wav', 'wb')

obj_new.setnchannels(1)
obj_new.setsampwidth(2)
obj_new.setframerate(16000.0)

obj_new.writeframes(frames)

obj_new.close()
